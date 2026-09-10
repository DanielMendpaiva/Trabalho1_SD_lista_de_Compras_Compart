# Trabalho 1 SD - gRPC Tarefas

Projeto da atividade de gRPC/Protocol Buffers da disciplina de Sistemas Distribuidos.
Tem um servidor gRPC que guarda as tarefas e um cliente de linha de comando pra mexer nelas.

## Pastas

- protos -> o .proto do projeto
- server -> codigo do servidor
- client -> codigo do cliente
- docker-compose.yml

## Rodando com docker (mais facil)

na raiz do projeto roda:

**docker compose up --build**

vai subir o servidor e 2 clientes, cada um com IP fixo:
servidor 172.25.0.10
cliente1 172.25.0.11
cliente2 172.25.0.12

os clientes ficam esperando entrada no terminal, entao pra usar o menu deles tem que dar
attach em outro terminal, tipo:

**docker attach nome_do_container_cliente1**

(pra saber o nome certo do container é só rodar **docker ps** antes)

pra parar td:

**docker compose down**

## Rodando sem docker

servidor:

**cd server**
**pip install -r requirements.txt**
**python server.py**

cliente (outro terminal):

**cd client**
**pip install -r requirements.txt**
**python client.py**

por padrao o cliente tenta conectar em localhost:50051. se for testar com servidor em
outra maquina/IP, definir a variavel antes de rodar:

**export SERVIDOR_ENDERECO=IP_DO_SERVIDOR:50051**
**python client.py**

(no windows é **set** em vez de **export**)

## Caso precise gerar o .proto de novo

Se mexer no arquivo tarefas.proto precisa recompilar pra atualizar os arquivos gerados,
comando:

**python -m grpc_tools.protoc -I=protos --python_out=server --grpc_python_out=server protos/tarefas.proto**
**python -m grpc_tools.protoc -I=protos --python_out=client --grpc_python_out=client protos/tarefas.proto**

roda os dois, um pra cada pasta (server e client), porque os dois precisam do codigo gerado.

## O que da pra fazer no cliente

1 - Criar Tarefa
2 - Listar Tarefas
3 - Atualizar Tarefa
4 - Deletar Tarefa
0 - Sair

As tarefa ficam salvas no servidor em arquivos .json (uma tarefa = um arquivo), dentro
da pasta server/tarefas_db, que é criada automatico quando o servidor sobe.
