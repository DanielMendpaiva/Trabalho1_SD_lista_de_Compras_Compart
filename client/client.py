import os
import sys

import grpc
import tarefas_pb2
import tarefas_pb2_grpc

ENDERECO = os.environ.get("SERVIDOR_ENDERECO", "localhost:50051")


def imprimir(t):
    print(t.id, "-", t.titulo, "-", t.status)
    print("   ", t.descricao)
    print("    prazo:", t.data_limite, "| responsaveis:", ", ".join(t.responsaveis))


def main():
    if len(sys.argv) < 2:
        print("uso: python client.py [criar|listar|atualizar|deletar] ...")
        return

    canal = grpc.insecure_channel(ENDERECO)
    stub = tarefas_pb2_grpc.TarefaServiceStub(canal)
    cmd = sys.argv[1]

    if cmd == "criar":
        titulo, desc, status, prazo, resp = sys.argv[2:7]
        t = stub.CriarTarefa(tarefas_pb2.CriarTarefaRequest(
            titulo=titulo, descricao=desc, status=status,
            data_limite=prazo, responsaveis=resp.split(",")))
        imprimir(t)

    elif cmd == "listar":
        resp = stub.ListarTarefas(tarefas_pb2.Vazio())
        if not resp.tarefas:
            print("nenhuma tarefa cadastrada")
        for t in resp.tarefas:
            imprimir(t)

    elif cmd == "atualizar":
        id, titulo, desc, status, prazo, resp = sys.argv[2:8]
        t = stub.AtualizarTarefa(tarefas_pb2.Tarefa(
            id=id, titulo=titulo, descricao=desc, status=status,
            data_limite=prazo, responsaveis=resp.split(",")))
        imprimir(t)

    elif cmd == "deletar":
        id = sys.argv[2]
        r = stub.DeletarTarefa(tarefas_pb2.DeletarTarefaRequest(id=id))
        print(r.mensagem)

    else:
        print("comando invalido")


if __name__ == "__main__":
    main()