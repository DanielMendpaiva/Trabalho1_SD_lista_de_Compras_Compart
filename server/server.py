import os
import json
import threading

import grpc
import tarefas_pb2
import tarefas_pb2_grpc

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tarefas_db")
os.makedirs(PASTA, exist_ok=True)


def novo_id():
    return os.urandom(16).hex()


# grpc precisa de um executor com interface parecida com a do
# concurrent.futures, entao foi feita essa versao simples na mao
class Futuro:
    def __init__(self):
        self.cond = threading.Condition()
        self.pronto = False
        self.valor = None
        self.erro = None
        self.callbacks = []

    def concluir(self, valor=None, erro=None):
        with self.cond:
            self.valor = valor
            self.erro = erro
            self.pronto = True
            self.cond.notify_all()
            cbs = list(self.callbacks)
        for cb in cbs:
            cb(self)

    def add_done_callback(self, fn):
        with self.cond:
            if not self.pronto:
                self.callbacks.append(fn)
                return
        fn(self)

    def result(self, timeout=None):
        with self.cond:
            self.cond.wait_for(lambda: self.pronto, timeout=timeout)
        if self.erro:
            raise self.erro
        return self.valor

    def done(self):
        return self.pronto

    def cancel(self):
        return False

    def cancelled(self):
        return False

    def running(self):
        return not self.pronto


class Executor:
    def submit(self, fn, *args, **kwargs):
        f = Futuro()

        def alvo():
            try:
                f.concluir(valor=fn(*args, **kwargs))
            except Exception as e:
                f.concluir(erro=e)

        threading.Thread(target=alvo, daemon=True).start()
        return f


class Servico(tarefas_pb2_grpc.TarefaServiceServicer):

    def caminho(self, id):
        return os.path.join(PASTA, id + ".json")

    def CriarTarefa(self, req, ctx):
        id = novo_id()
        t = {
            "id": id,
            "titulo": req.titulo,
            "descricao": req.descricao,
            "status": req.status,
            "data_limite": req.data_limite,
            "responsaveis": list(req.responsaveis),
        }
        with open(self.caminho(id), "w") as f:
            json.dump(t, f)
        return tarefas_pb2.Tarefa(**t)

    def ListarTarefas(self, req, ctx):
        lista = []
        for nome in os.listdir(PASTA):
            if not nome.endswith(".json"):
                continue
            with open(os.path.join(PASTA, nome)) as f:
                lista.append(tarefas_pb2.Tarefa(**json.load(f)))
        return tarefas_pb2.ListaTarefas(tarefas=lista)

    def AtualizarTarefa(self, req, ctx):
        caminho = self.caminho(req.id)
        if not os.path.exists(caminho):
            ctx.set_code(grpc.StatusCode.NOT_FOUND)
            ctx.set_details("tarefa nao encontrada")
            return tarefas_pb2.Tarefa()

        t = {
            "id": req.id,
            "titulo": req.titulo,
            "descricao": req.descricao,
            "status": req.status,
            "data_limite": req.data_limite,
            "responsaveis": list(req.responsaveis),
        }
        with open(caminho, "w") as f:
            json.dump(t, f)
        return tarefas_pb2.Tarefa(**t)

    def DeletarTarefa(self, req, ctx):
        caminho = self.caminho(req.id)
        if os.path.exists(caminho):
            os.remove(caminho)
            return tarefas_pb2.DeletarTarefaResponse(sucesso=True, mensagem="tarefa removida")
        return tarefas_pb2.DeletarTarefaResponse(sucesso=False, mensagem="tarefa nao encontrada")


def main():
    server = grpc.server(Executor())
    tarefas_pb2_grpc.add_TarefaServiceServicer_to_server(Servico(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("servidor rodando na porta 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    main()