import threading
import requests
import psycopg2

API_URL = "http://positivo-server:8000"
DB_CONFIG = {
    "host": "positivo-server",
    "database": "bookinghub",
    "user": "admin",
    "password": "admin",
    "port": 5433 # Usando a porta 5433 exposta para o host de acordo com o seed.py
}

def setup_test_flight(available_seats=5):
    """
    Cria um voo temporário para o teste com uma quantidade específica de assentos disponíveis.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    # Pega um cliente e dois aeroportos existentes
    cur.execute("SELECT id FROM customers LIMIT 1;")
    customer_id = cur.fetchone()[0]
    
    cur.execute("SELECT id FROM airports LIMIT 2;")
    airports = cur.fetchall()
    origin_id = airports[0][0]
    dest_id = airports[1][0]
    
    # Cria um voo de teste
    cur.execute('''
        INSERT INTO flights (flight_number, origin_airport_id, destination_airport_id, departure_time, arrival_time, total_seats, available_seats, price)
        VALUES ('TEST01', %s, %s, NOW() + INTERVAL '1 day', NOW() + INTERVAL '1 day 2 hours', %s, %s, 500.00)
        RETURNING id;
    ''', (origin_id, dest_id, available_seats, available_seats))
    flight_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return customer_id, flight_id

def cleanup_test_flight(flight_id):
    """
    Remove o voo de teste e suas reservas associadas.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("DELETE FROM flight_reservations WHERE flight_id = %s;", (flight_id,))
    cur.execute("DELETE FROM flights WHERE id = %s;", (flight_id,))
    conn.commit()
    cur.close()
    conn.close()

def test_overbooking():
    print("Iniciando teste de OVERBOOKING (Condição de Corrida na Quantidade de Assentos)...")
    # Configura um voo com apenas 5 assentos disponíveis
    customer_id, flight_id = setup_test_flight(available_seats=5)
    
    threads = []
    results = []
    
    def make_reservation(seat_number):
        payload = {
            "customer_id": customer_id,
            "flight_id": flight_id,
            "seat_number": seat_number
        }
        try:
            response = requests.post(f"{API_URL}/reservas/voo", json=payload)
            results.append((seat_number, response.status_code, response.json()))
        except Exception as e:
            results.append((seat_number, 500, str(e)))

    # Tenta fazer 10 reservas simultâneas (o voo só tem 5 lugares)
    # Assentos diferentes são usados para garantir que o problema não seja "Assento já reservado", mas sim "Voo lotado"
    for i in range(10):
        t = threading.Thread(target=make_reservation, args=(i+1,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    sucessos = len([r for r in results if r[1] == 200])
    falhas_lotado = len([r for r in results if r[1] == 400 and r[2].get('detail') == 'Voo lotado'])
    
    print(f"[{'PASSOU' if sucessos == 5 else 'FALHOU'}] Teste Overbooking")
    print(f" -> Sucessos: {sucessos} (Esperado: 5)")
    print(f" -> Falhas (Voo lotado): {falhas_lotado} (Esperado: 5)")
    
    cleanup_test_flight(flight_id)
    print("-" * 50)

def test_concurrency_same_seat():
    print("Iniciando teste de CONCORRÊNCIA (Mesmo Assento)...")
    # Configura um voo com muitos assentos, o conflito será no mesmo assento
    customer_id, flight_id = setup_test_flight(available_seats=50)
    
    threads = []
    results = []
    
    def make_reservation():
        payload = {
            "customer_id": customer_id,
            "flight_id": flight_id,
            "seat_number": 99 # Todos tentam reservar exatamente o mesmo assento
        }
        try:
            response = requests.post(f"{API_URL}/reservas/voo", json=payload)
            results.append((response.status_code, response.json()))
        except Exception as e:
            results.append((500, str(e)))

    # Tenta fazer 5 reservas simultâneas para O MESMO assento
    for _ in range(5):
        t = threading.Thread(target=make_reservation)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    sucessos = len([r for r in results if r[0] == 200])
    falhas_assento = len([r for r in results if r[0] == 400 and r[1].get('detail') == 'Assento já reservado'])
    
    print(f"[{'PASSOU' if sucessos == 1 else 'FALHOU'}] Teste Concorrência de Assento")
    print(f" -> Sucessos: {sucessos} (Esperado: 1)")
    print(f" -> Falhas (Assento já reservado): {falhas_assento} (Esperado: 4)")
    
    cleanup_test_flight(flight_id)
    print("-" * 50)

if __name__ == "__main__":
    test_overbooking()
    test_concurrency_same_seat()
