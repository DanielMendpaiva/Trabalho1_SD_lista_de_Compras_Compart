# Usa a mesma imagem oficial do Python 3.11 como base do cliente
FROM python:3.11

# Cria e entra na pasta de trabalho /app dentro do container do cliente
WORKDIR /app

# Copia todos os arquivos da pasta client do seu computador para dentro do container
COPY . .

# Instala as bibliotecas necessarias listadas no requirements do cliente
RUN pip install -r requirements.txt

CMD ["python", "-u", "server.py"]