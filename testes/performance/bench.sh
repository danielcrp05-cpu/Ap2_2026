#!/usr/bin/env bash

HOST="${1:-localhost}"
USER="admin"
PORT="5433"
DB="bookinghub"

# Remove cache
docker restart ap2_postgres
sync; echo 3 | sudo tee /proc/sys/vm/drop_caches

# Initialize database
pgbench -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --initialize --scale=10

# Run queries
pgbench -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/voos_disponiveis_filtro.sql > voos_disponiveis_filtro.log
pgbench -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/taxa_ocupacao_voo.sql > taxa_ocupacao_voo.log
pgbench -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/quartos_disponiveis_sem_conflito.sql > quartos_disponiveis_sem_conflito.log
pgbench -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/historico_completo_cliente.sql > historico_completo_cliente.log

# Remove cache
docker restart ap2_postgres
sync; echo 3 | sudo tee /proc/sys/vm/drop_caches

# Enable indexes
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f indices.sql

# Run queries with indexes
pgbench -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/voos_disponiveis_filtro.sql > voos_disponiveis_filtro_com_indices.log
pgbench -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/taxa_ocupacao_voo.sql > taxa_ocupacao_voo_com_indices.log
pgbench -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/quartos_disponiveis_sem_conflito.sql > quartos_disponiveis_sem_conflito_com_indices.log
pgbench -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/historico_completo_cliente.sql > historico_completo_cliente_com_indices.log