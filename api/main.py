import psycopg2
import psycopg2, random, time
from fastapi import FastAPI, HTTPException
from datetime import date
from pydantic import BaseModel

class pagamento(BaseModel):
    reservation_id: int
    reservation_type: str
    amount: float
    payment_method: str

class reserva_voo(BaseModel):
    customer_id: int
    flight_id: int
    seat_number: int

app = FastAPI()

def get_db_conn():
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="bookinghub",
            user="admin",
            password="admin",
            port=5432
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados")

def executar(fn:callable, args):
    conn = get_db_conn()
    for tentativa in range(3):
        try:
            with conn.cursor() as cur:
                return fn(cur, args)
        except psycopg2.errors.SerializationFailure:
            conn.rollback()
            espera = (2 ** tentativa) * 0.1 + random.uniform(0, 0.05)
            time.sleep(espera)
            continue
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Erro na função {fn.__name__}: {e}")
            raise HTTPException(status_code=500, detail="Erro ao executar operação")
        finally:
            conn.close()
    else:
        print(f"Erro de serialização na função {fn.__name__}")
        raise HTTPException(status_code=500, detail="Erro ao executar operação")            


@app.get("/")
def home():
    return {"message": "API funcionando"}

@app.get("/voos/disponiveis")
def get_voos():
    """
    Lista voos disponíveis com filtros por origem, destino e data;
    """
    def _get_voos(cur, args):
        cur.execute(
            """
            SELECT
                o.city AS origem,
                d.city AS destino,
                f.departure_time AS data_partida,
                f.arrival_time AS data_chegada
            FROM
                flights f
                JOIN airports o ON f.origin_airport_id = o.id
                JOIN airports d ON f.destination_airport_id = d.id
            """
        )
        return cur.fetchall()
    
    return executar(_get_voos, None)

@app.get("/hoteis/disponiveis")
def get_hoteis(data_inicio: date, data_fim: date):
    """
    Lista hotéis com quartos livres para um período;
    """
    def _get_hoteis(cur, args):
        cur.execute(
            f"""
            SELECT
                r.id AS room_id,
                r.hotel_id
            FROM
                rooms r
            WHERE
                NOT EXISTS (
                    SELECT
                        1
                    FROM
                        hotel_reservations hr
                    WHERE
                        hr.room_id = r.id
                        AND hr.status IN ('confirmed', 'pending')
                        AND hr.check_in < '{data_fim}' :: date
                        AND hr.check_out > '{data_inicio}' :: date
                );
            """
        )
        return cur.fetchall()
    
    return executar(_get_hoteis, None)

@app.get("/clientes/{id}/reservas")
def get_reservas(id: int):
    """
    Retorna todas as reservas (voos e hoteis) de um cliente com histórico de pagamentos;
    """
    def _get_reservas(cur, args):
        cur.execute(
            f"""
            WITH all_customer_reservations AS (
                SELECT 
                    id AS reservation_id, 
                    'flight' AS reservation_type, 
                    flight_id AS item_id, 
                    customer_id, 
                    status AS reservation_status
                FROM flight_reservations
                WHERE customer_id = {id}

                UNION ALL

                SELECT 
                    id AS reservation_id, 
                    'hotel' AS reservation_type, 
                    room_id AS item_id, 
                    customer_id, 
                    status AS reservation_status
                FROM hotel_reservations
                WHERE customer_id = {id}
            )
            SELECT 
                r.reservation_type,
                r.reservation_id,
                r.item_id,
                r.reservation_status,
                p.id AS payment_id,
                p.amount,
                p.payment_method,
                p.status AS payment_status
            FROM 
                all_customer_reservations r
            INNER JOIN 
                payments p ON r.reservation_id = p.reservation_id AND r.reservation_type = p.reservation_type;
            """
        )
        return cur.fetchall()
    
    return executar(_get_reservas, None)

@app.get("/relatorios/ocupacao")
def get_ocupacao(tipo_reserva: str, data_inicio: date, data_fim: date):
    """
    Retorna taxa de ocupação por voo e por quarto de hotel em um período;
    """

@app.post("/reservas/voo")
def criar_reserva_voo(reserva: reserva_voo):
    """
    Cria reserva de voo com controle de concorrência;
    """
    def _criar_reserva_voo(cur, args):
        cur.execute(
            """
            SELECT available_seats FROM flights WHERE id = %s FOR UPDATE;
            """,
            (reserva.flight_id,)
        )
        flight = cur.fetchone()
        
        if not flight:
            raise HTTPException(status_code=404, detail="Voo não encontrado")
            
        if flight[0] <= 0:
            raise HTTPException(status_code=400, detail="Voo lotado")
            
        cur.execute(
            """
            SELECT id FROM flight_reservations 
            WHERE flight_id = %s AND seat_number = %s AND status != 'cancelled';
            """,
            (reserva.flight_id, str(reserva.seat_number))
        )
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Assento já reservado")

        cur.execute(
            """
            UPDATE flights SET available_seats = available_seats - 1 WHERE id = %s;
            """,
            (reserva.flight_id,)
        )
        
        cur.execute(
            """
            INSERT INTO flight_reservations (customer_id, flight_id, seat_number, status, created_at, updated_at)
            VALUES (%s, %s, %s, 'pending', NOW(), NOW()) RETURNING id;
            """,
            (reserva.customer_id, reserva.flight_id, str(reserva.seat_number))
        )
        reservation_id = cur.fetchone()[0]
        if not reservation_id:
            raise HTTPException(status_code=400, detail="Erro ao criar reserva")
        cur.connection.commit()
        return {"message": "Reserva criada com sucesso", "reservation_id": reservation_id}

    return executar(_criar_reserva_voo, None)

@app.post("/reservas/hotel")
def criar_reserva_hotel():
    """
    Cria reserva de hotel verificando conflito de datas;
    """

@app.post("/pagamentos")
def criar_pagamentos(payment: pagamento):
    """
    Registra pagamento e confirma a reserva;
    """
    if payment.reservation_type not in ["flight", "hotel"]:
        raise HTTPException(status_code=400, detail="Tipo de reserva inválido")
    if payment.payment_method not in ["credit_card", "boleto", "pix"]:
        raise HTTPException(status_code=400, detail="Método de pagamento inválido")
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Valor do pagamento inválido")

    # Check if reservation exists
    if payment.reservation_type == "flight":
        tabela = "flight_reservations"
    elif payment.reservation_type == "hotel":
        tabela = "hotel_reservations"
    else:
        raise HTTPException(status_code=400, detail="Tipo de reserva inválido")
    def _criar_pagamentos(cur, args):
        cur.execute(
            f"""
            SELECT
                id
            FROM
                {tabela}
            WHERE
                id = {payment.reservation_id};
            """
        )

        reservation = cur.fetchone()
        if not reservation:
            raise HTTPException(status_code=404, detail="Reserva não encontrada")

        cur.execute(
            f"""
            INSERT INTO payments (reservation_id, reservation_type, amount, payment_method, status, created_at)
            VALUES ({payment.reservation_id}, '{payment.reservation_type}', {payment.amount}, '{payment.payment_method}', 'pending', NOW());
            """
        )
        cur.connection.commit()
        return {"message": "Pagamento registrado com sucesso"}

    return executar(_criar_pagamentos, None)

@app.delete("/reservas/{id}")
def deletar_reserva(id: int, tipo: str):
    """
    Cancela reserva e estorna disponibilidade;
    """
    if tipo == "voo":
        tabela = "flight_reservations"
    elif tipo == "hotel":
        tabela = "hotel_reservations"
    else:
        raise HTTPException(status_code=400, detail="Tipo de reserva inválido")
    def _deletar_reserva(cur, args):
        cur.execute(
            f"""
            DELETE FROM {tabela} WHERE id = {id} RETURNING id;
            """
        )
        deleted_row = cur.fetchone()
        if not deleted_row:
            raise HTTPException(status_code=404, detail="Reserva não encontrada")
        cur.connection.commit()
        return {"message": "Reserva cancelada"}

    return executar(_deletar_reserva, None)

@app.post("/test/falha-transacao")
def falha_transacao():
    """
    Testa falha na transação;
    """
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO payments (reservation_id, reservation_type, amount, payment_method, status, created_at) VALUES (1, 'voo', 1, 'credit_card', 'pending', NOW());"
            )
            raise Exception("Teste falha de transação")
    except Exception as e:
        conn.rollback()
        print(f"Erro: {e}")
        raise HTTPException(status_code=500, detail="Teste concluído com sucesso")