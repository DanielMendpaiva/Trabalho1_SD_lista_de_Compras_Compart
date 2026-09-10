import os
import grpc
import tarefas_pb2
import tarefas_pb2_grpc

ENDERECO = os.environ.get("SERVIDOR_ENDERECO", "localhost:50051")

def imprimir(t):
    print(f"\n[{t.id}] {t.titulo} - {t.status}")
    print(f" Descricao: {t.descricao}")
    print(f" Prazo: {t.data_limite} | Responsaveis: {', '.join(t.responsaveis)}")

def menu():
    print("\nGERENCIADOR DE TAREFAS:")
    print("1. Criar Tarefa")
    print("2. Listar Tarefas")
    print("3. Atualizar Tarefa")
    print("4. Deletar Tarefa")
    print("0. Sair")
    return input("Escolha uma opcao: ").strip()

def main():
    canal = grpc.insecure_channel(ENDERECO)
    stub = tarefas_pb2_grpc.TarefaServiceStub(canal)

    while True:
        opcao = menu()

        if opcao == "1":
            titulo = input("Titulo: ")
            desc = input("Descricao: ")
            status = input("Status: ")
            prazo = input("Prazo: ")
            resp = input("Responsaveis (separados por virgula): ")
            t = stub.CriarTarefa(tarefas_pb2.CriarTarefaRequest(
                titulo=titulo, descricao=desc, status=status,
                data_limite=prazo, responsaveis=resp.split(",")))
            imprimir(t)

        elif opcao == "2":
            resp = stub.ListarTarefas(tarefas_pb2.Vazio())
            if not resp.tarefas:
                print("\nNenhuma tarefa cadastrada.")
            for t in resp.tarefas:
                imprimir(t)

        elif opcao == "3":
            id_tarefa = input("ID da tarefa a atualizar: ")
            titulo = input("Novo Titulo: ")
            desc = input("Nova Descricao: ")
            status = input("Novo Status: ")
            prazo = input("Novo Prazo: ")
            resp = input("Novos Responsaveis (separados por virgula): ")
            t = stub.AtualizarTarefa(tarefas_pb2.Tarefa(id=id_tarefa, titulo=titulo, descricao=desc, status=status, data_limite=prazo, responsaveis=resp.split(",")))
            imprimir(t)

        elif opcao == "4":
            id_tarefa = input("ID da tarefa a deletar: ")
            r = stub.DeletarTarefa(tarefas_pb2.DeletarTarefaRequest(id=id_tarefa))
            print(f"\n{r.mensagem}")

        elif opcao == "0":
            print("\nSaindo...")
            break
        
        else:
            print("\nOpcao invalida.")

if __name__ == "__main__":
    main()