cd %PROGRAMFILES%\PostgreSQL\18\bin || exit


pgbench -U "admin" -d "bookinghub" -h "localhost" -p 5433 -U "admin" -i -s 10

pgbench -U "admin" -d "bookinghub" -c 10 -j 3 -T 30 -f query_voos.sql

pgbench -U "admin" -d "bookinghub" -c 10 -j 3 -T 30 -f query_disponibilidade.sql