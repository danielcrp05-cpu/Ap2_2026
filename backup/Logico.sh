#!/usr/bin/env bash

# Database Connection
HOST='localhost'
PORT='5433'
USER='admin'
export PGPASSWORD='admin'

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "Backup> Fazendo dump do banco bookinghub...${NC}"
if pg_dump --host="$HOST" --port="$PORT" --username="$USER" --dbname="bookinghub" --file="backup.dump" --format=c; then
    echo -e "${GREEN}Backup> Dump realizado com sucesso!${NC}"
    sleep 2
else
    echo -e "${RED}Backup> Dump falhou!${NC}"
    sleep 3
    exit 1
fi

echo -e "Backup> Criando novo banco para restaurar${NC}"
if psql --host="$HOST" --port="$PORT" --username="$USER" --dbname="postgres" --command="CREATE DATABASE bookinghub_restored;" ; then
    echo -e "${GREEN}Backup> Banco criado com sucesso!${NC}"
    sleep 2
else
    echo -e "${RED}Backup> Criação do banco falhou!${NC}"
    sleep 3
    exit 1
fi

echo -e "Backup> Restaurando banco bookinghub_restored...${NC}"
if pg_restore --host="$HOST" --port="$PORT" --username="$USER" --dbname="bookinghub_restored" backup.dump; then
    echo -e "${GREEN}Backup> Restauração realizada com sucesso!${NC}"
    sleep 2
else
    echo -e "${RED}Backup> Restauração falhou!${NC}"
    sleep 3
    exit 1
fi

echo -e "Backup> Contando registros de voos...${NC}"
if psql --host="$HOST" --port="$PORT" --username="$USER" --dbname="bookinghub_restored" --command="SELECT COUNT(*) FROM flights;" ; then
    echo -e "${GREEN}Backup> Contagem realizada com sucesso!${NC}"
    sleep 2
else
    echo -e "${RED}Backup> Contagem falhou!${NC}"
    sleep 3
    exit 1
fi

echo -e "Backup> Removendo banco restaurado...${NC}"
if psql --host="$HOST" --port="$PORT" --username="$USER" --dbname="postgres" --command="DROP DATABASE bookinghub_restored;" ; then
    echo -e "${GREEN}Backup> Banco removido com sucesso!${NC}"
    sleep 2
else
    echo -e "${RED}Backup> Remoção do banco falhou!${NC}"
    sleep 3
    exit 1
fi

echo -e "Backup> Removendo arquivo de dump...${NC}"
if rm backup.dump; then
    echo -e "${GREEN}Backup> Arquivo de dump removido com sucesso!${NC}"
    sleep 2
else
    echo -e "${RED}Backup> Remoção do arquivo de dump falhou!${NC}"
    sleep 3
    exit 1
fi