# Usa uma imagem oficial do Python 3.11 do Docker Hub como base do sistema
FROM python:3.11

# Cria e define a pasta /app dentro do container como a pasta onde tudo vai acontecer
WORKDIR /app

# Copia todos os arquivos da pasta server do seu computador para a pasta /app do container
COPY . .

# Executa o instalador de pacotes dentro do container para baixar as dependencias
RUN pip install -r requirements.txt

CMD ["python", "client.py"]