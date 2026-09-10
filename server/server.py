import os
import json

import grpc
import tarefas_pb2
import tarefas_pb2_grpc

# Pasta onde cada tarefa é salva como um arquivo <id>.json
PASTA_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tarefas_db")

# Garante que a pasta de armazenamento existe antes do servidor subir
os.makedirs(PASTA_DB, exist_ok=True)

class TarefaServiceServicer(tarefas_pb2_grpc.TarefaServiceServicer):
    def _caminho_arquivo(self, id_tarefa: str) -> str:
        """Monta o caminho completo do arquivo de uma tarefa a partir do id."""
        return os.path.join(PASTA_DB, f"{id_tarefa}.json")

    def _tarefa_para_dict(self, tarefa_msg) -> dict:
        """Converte uma mensagem protobuf Tarefa em dict serializável."""
        return {
            "id": tarefa_msg.id,
            "titulo": tarefa_msg.titulo,
            "descricao": tarefa_msg.descricao,
            "status": tarefa_msg.status,
            "data_limite": tarefa_msg.data_limite,
            "responsaveis": list(tarefa_msg.responsaveis),
        }

    def _salvar(self, dados: dict) -> None:
        """Grava o dict da tarefa em disco, em arquivo próprio."""
        caminho = self._caminho_arquivo(dados["id"])
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def _carregar(self, id_tarefa: str):
        """Lê uma tarefa do disco. Retorna None se o arquivo não existir."""
        caminho = self._caminho_arquivo(id_tarefa)
        if not os.path.exists(caminho):
            return None
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    # ---------------- RPCs ----------------

    def CriarTarefa(self, request, context):
        # Utiliza o ID fornecido na request já que o UUID foi removido
        id_tarefa = request.id
        
        dados = {
            "id": id_tarefa,
            "titulo": request.titulo,
            "descricao": request.descricao,
            "status": request.status,
            "data_limite": request.data_limite,
            "responsaveis": list(request.responsaveis),
        }
        self._salvar(dados)
        print(f"[CriarTarefa] Tarefa criada: {id_tarefa} - {dados['titulo']}")
        return tarefas_pb2.Tarefa(**dados)

    def ListarTarefas(self, request, context):
        tarefas = []
        # os.listdir percorre todos os arquivos da pasta de armazenamento
        for nome_arquivo in os.listdir(PASTA_DB):
            if not nome_arquivo.endswith(".json"):
                continue
            caminho = os.path.join(PASTA_DB, nome_arquivo)
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                tarefas.append(tarefas_pb2.Tarefa(**dados))
        print(f"[ListarTarefas] {len(tarefas)} tarefa(s) encontrada(s)")
        return tarefas_pb2.ListaTarefas(tarefas=tarefas)

    def AtualizarTarefa(self, request, context):
        existente = self._carregar(request.id)
        if existente is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Tarefa com id '{request.id}' não encontrada")
            return tarefas_pb2.Tarefa()

        dados = self._tarefa_para_dict(request)
        self._salvar(dados)
        print(f"[AtualizarTarefa] Tarefa atualizada: {dados['id']}")
        return tarefas_pb2.Tarefa(**dados)

    def DeletarTarefa(self, request, context):
        caminho = self._caminho_arquivo(request.id)
        if os.path.exists(caminho):
            os.remove(caminho)
            print(f"[DeletarTarefa] Tarefa removida: {request.id}")
            return tarefas_pb2.DeletarTarefaResponse(
                sucesso=True, mensagem="Tarefa removida com sucesso"
            )

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"Tarefa com id '{request.id}' não encontrada")
        return tarefas_pb2.DeletarTarefaResponse(
            sucesso=False, mensagem="Tarefa não encontrada"
        )


def serve(thread_pool, porta: str = "50051"):
    # Recebe o executor via parâmetro de quem importar este módulo
    servidor = grpc.server(thread_pool)
    tarefas_pb2_grpc.add_TarefaServiceServicer_to_server(
        TarefaServiceServicer(), servidor
    )
    # necessário para a demonstração entre máquinas com IPs distintos
    servidor.add_insecure_port(f"[::]:{porta}")
    servidor.start()
    print(f"Servidor gRPC rodando na porta {porta}...")
    print(f"Armazenando tarefas em: {PASTA_DB}")
    servidor.wait_for_termination()


if __name__ == "__main__":

    pass