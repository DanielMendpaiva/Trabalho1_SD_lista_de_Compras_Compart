import grpc
import os
import sys
import uuid

import tarefas_pb2
import tarefas_pb2_grpc

SERVIDOR_END = os.environ.get('SERVIDOR_END', 'localhost:50051')

def imprimir_lista_de_compras(t):
    print(f" id : {t.id}")
    print(f" titulo : {t.titulo}")
    print(f" descricao : {t.descricao}")
    print(f" status : {t.status}")
    print(f" data_limite : {t.data_limite}")
    print(f" responsavel :  {', '.join(t.responsaveis)}")
    print("-" * 40)

def criar(stub, titulo, descricao, status, data_limite, responsavel):
    responsaveis = [r.strip() for r in responsavel.split(',') if r.strip()]
    id_tarefa = str(uuid.uuid4())
    
    t = tarefas_pb2.Tarefa(
        id=id_tarefa,
        titulo=titulo,
        descricao=descricao,
        status=status,
        data_limite=data_limite,
        responsaveis=responsaveis
    )

    resposta = stub.CriarTarefa(t)
    print(f"Tarefa criada com sucesso! ID: {resposta.id}")

def listar(stub):
    # Passando a request vazia correta conforme gerado pelo protobuf
    resposta = stub.ListarTarefas(tarefas_pb2.ListarTarefasRequest())

    if not resposta.tarefas:
        print("Nenhuma tarefa encontrada.")
        return

    for t in resposta.tarefas:
        imprimir_lista_de_compras(t)

def atualizar(stub, id_tarefa, titulo, descricao, status, data_limite, responsavel):
    responsaveis = [r.strip() for r in responsavel.split(',') if r.strip()]

    t = tarefas_pb2.Tarefa(
        id=id_tarefa,
        titulo=titulo,
        descricao=descricao,
        status=status,
        data_limite=data_limite,
        responsaveis=responsaveis
    )

    try:
        resposta = stub.AtualizarTarefa(t)
        print(f"Tarefa atualizada com sucesso! ID: {resposta.id}")
    except grpc.RpcError as e:
        print(f"Falha ao atualizar a tarefa: {e.details()}")

def deletar(stub, id_tarefa):
    try:
        resposta = stub.DeletarTarefa(tarefas_pb2.DeletarTarefaRequest(id=id_tarefa))
        if resposta.sucesso:
            print("Tarefa deletada com sucesso!")
        else:
            print(f"Falha: {resposta.mensagem}")
    except grpc.RpcError as e:
        print(f"Falha ao deletar a tarefa: {e.details()}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
        
    comando = sys.argv[1]
    canal = grpc.insecure_channel(SERVIDOR_END)
    stub = tarefas_pb2_grpc.TarefaServiceStub(canal)
    print(f"Conectado ao servidor: {SERVIDOR_END}\n")

    if comando == "listar":
        listar(stub)
    elif comando == "criar":
        if len(sys.argv) != 7:
            print('Uso: python client.py criar "Titulo" "Descricao" "status" "data_limite" "resp1,resp2"')
            sys.exit(1)
        criar(stub, *sys.argv[2:7])
    elif comando == "atualizar":
        if len(sys.argv) != 8:
            print('Uso: python client.py atualizar <id> "Titulo" "Descricao" "status" "data_limite" "resp1,resp2"')
            sys.exit(1)
        atualizar(stub, *sys.argv[2:8])
    elif comando == "deletar":
        if len(sys.argv) != 3:
            print("Uso: python client.py deletar <id>")
            sys.exit(1)
        deletar(stub, sys.argv[2])
    else:
        print(f"Comando desconhecido: {comando}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()