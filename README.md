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

## 4. Teste de Overbooking e Concorrência

Para testar o overbooking e a concorrência, utilize o script `overbooking_e_concorrencia.py` na raiz do repositório clonado. Dentro do script há algumas variáveis de configuração.

```bash
python -m pip install requests psycopg2
python ./testes/overbooking_e_concorrencia.py
```

## 5. Benchmark dos índices

O script assume que ele seja executado em um ambiente Linux no mesmo servidor que os contêineres e com acesso root, para realizar a limpeza dos caches. Dentro do script há algumas variáveis de configuração.

```bash
sudo ./testes/performance/bench.sh
```

## 6. Teste de backup lógico

O script assume que é possível criar uma conexão ao banco de dados. Dentro do script há algumas variáveis de configuração.

```bash
./backup/Logico.sh
```
