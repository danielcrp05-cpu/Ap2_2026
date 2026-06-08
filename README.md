# Banco de Dados: Trabalho Final

BookingHub: Plataforma de Reservas com Alta Concorrência

## 1. Contêineres Docker

Para executar os contêineres Docker, que executam o banco de dados e a API, utilize o seguinte comando na raiz do repositório clonado:

```bash
docker compose up -d
```

## 2. Configuração do Banco de Dados

O contêiner do banco de dados possui as tabelas necessárias preconfiguradas. Portanto, precisamos apenas popular as tabelas com dados utilizando o script `seed.py` na raiz do repositório clonado.

```bash
pip install -r requirements.txt
python seed.py
```

## 3. Acesso à API

A API web pode ser acessada em <http://localhost:8000/docs>
