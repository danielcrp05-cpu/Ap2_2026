#!/usr/bin/env bash

HOST="${1:-localhost}"
USER="admin"
export PGPASSWORD='admin'
PORT="5433"
DB="bookinghub"

limpar_cache() {
    echo "> Limpando cache..."
    docker restart ap2_postgres
    sync; echo 3 |  tee /proc/sys/vm/drop_caches
    sleep 5
}

# Create folders
if [ ! -d "sem_indices" ]; then
    mkdir sem_indices || exit 1
fi

if [ ! -d "com_indices" ]; then
    mkdir com_indices || exit 1
fi

echo ">> Realizando benchmark sem índices"
limpar_cache

echo "> Executando consultas com pgbench..."
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/voos_disponiveis_filtro.sql > sem_indices/voos_disponiveis_filtro.log
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/taxa_ocupacao_voo.sql > sem_indices/taxa_ocupacao_voo.log
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/quartos_disponiveis_sem_conflito.sql > sem_indices/quartos_disponiveis_sem_conflito.log
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/historico_completo_cliente.sql > sem_indices/historico_completo_cliente.log

limpar_cache

echo "> Modificando consultas..."
sed -i '1i EXPLAIN ANALYZE' consultas/*.sql

echo "> Executando consultas com psql..."
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/voos_disponiveis_filtro.sql > sem_indices/voos_disponiveis_filtro_explain.log
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/taxa_ocupacao_voo.sql > sem_indices/taxa_ocupacao_voo_explain.log
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/quartos_disponiveis_sem_conflito.sql > sem_indices/quartos_disponiveis_sem_conflito_explain.log
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/historico_completo_cliente.sql > sem_indices/historico_completo_cliente_explain.log

echo "> Revertendo consultas..."
sed -i '1d' consultas/*.sql

echo ">> Realizando benchmark com índices"
limpar_cache

echo "> Criando índices..."
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f indices.sql

echo "> Desativando sequencial scans..."
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -c "ALTER DATABASE bookinghub SET enable_seqscan = off;"

echo "> Executando consultas usando pgbench com índices..."
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/voos_disponiveis_filtro.sql > com_indices/voos_disponiveis_filtro.log
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/taxa_ocupacao_voo.sql > com_indices/taxa_ocupacao_voo.log
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/quartos_disponiveis_sem_conflito.sql > com_indices/quartos_disponiveis_sem_conflito.log
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/historico_completo_cliente.sql > com_indices/historico_completo_cliente.log

echo "> Modificando consultas..."
sed -i '1i EXPLAIN ANALYZE' consultas/*.sql

limpar_cache

echo "> Executando consultas usando psql com índices..."
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/voos_disponiveis_filtro.sql > com_indices/voos_disponiveis_filtro_explain.log
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/taxa_ocupacao_voo.sql > com_indices/taxa_ocupacao_voo_explain.log
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/quartos_disponiveis_sem_conflito.sql > com_indices/quartos_disponiveis_sem_conflito_explain.log
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/historico_completo_cliente.sql > com_indices/historico_completo_cliente_explain.log

echo "> Revertendo consultas..."
sed -i '1d' consultas/*.sql

echo "> Ativando sequencial scans..."
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -c "ALTER DATABASE bookinghub SET enable_seqscan = on;"

limpar_cache

echo "> Executando consultas usando pgbench com índices e seq scan..."
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/voos_disponiveis_filtro.sql > com_indices/voos_disponiveis_filtro_seqscan.log
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/taxa_ocupacao_voo.sql > com_indices/taxa_ocupacao_voo_seqscan.log
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/quartos_disponiveis_sem_conflito.sql > com_indices/quartos_disponiveis_sem_conflito_seqscan.log
pgbench -c 10 -j 2 -t 100 -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" --file=consultas/historico_completo_cliente.sql > com_indices/historico_completo_cliente_seqscan.log

echo "> Modificando consultas..."
sed -i '1i EXPLAIN ANALYZE' consultas/*.sql

limpar_cache

echo "> Executando consultas usando psql com índices e seq scan..."
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/voos_disponiveis_filtro.sql > com_indices/voos_disponiveis_filtro_explain_seqscan.log
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/taxa_ocupacao_voo.sql > com_indices/taxa_ocupacao_voo_explain_seqscan.log
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/quartos_disponiveis_sem_conflito.sql > com_indices/quartos_disponiveis_sem_conflito_explain_seqscan.log
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f consultas/historico_completo_cliente.sql > com_indices/historico_completo_cliente_explain_seqscan.log

echo "> Revertendo consultas..."
sed -i '1d' consultas/*.sql

echo "> Removendo índices..."
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -t -f find_indices.sql > drop_indices.sql
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DB" -f drop_indices.sql
rm drop_indices.sql
unset PGPASSWORD

echo ">>>>>>>> Benchmark finalizado! <<<<<<<<"