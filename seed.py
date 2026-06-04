import random
from datetime import datetime, timedelta

import psycopg2
from faker import Faker

fake = Faker('pt_BR')

# =========================
# CONFIGURAÇÃO DO BANCO
# =========================
conn = psycopg2.connect(
    host='localhost',
    database='bookinghub',
    user='admin',
    password='admin',
    port=5433
)

conn.autocommit = False
cur = conn.cursor()

# =========================
# DADOS BASE
# =========================
AIRPORTS = [
    ('GRU', 'Aeroporto Internacional de Guarulhos', 'São Paulo', 'Brasil'),
    ('CGH', 'Aeroporto de Congonhas', 'São Paulo', 'Brasil'),
    ('SDU', 'Santos Dumont', 'Rio de Janeiro', 'Brasil'),
    ('GIG', 'Galeão', 'Rio de Janeiro', 'Brasil'),
    ('BSB', 'Aeroporto de Brasília', 'Brasília', 'Brasil'),
    ('FOR', 'Pinto Martins', 'Fortaleza', 'Brasil'),
    ('REC', 'Guararapes', 'Recife', 'Brasil'),
    ('SSA', 'Deputado Luís Eduardo Magalhães', 'Salvador', 'Brasil'),
]

HOTEL_TYPES = ['single', 'double', 'suite']
RESERVATION_STATUS = ['pending', 'confirmed', 'cancelled']
PAYMENT_STATUS = ['pending', 'paid', 'refunded']
PAYMENT_METHODS = ['credit_card', 'pix', 'boleto']

# =========================
# LIMPAR TABELAS
# =========================
print('Limpando tabelas...')

cur.execute('DELETE FROM payments;')
cur.execute('DELETE FROM hotel_reservations;')
cur.execute('DELETE FROM flight_reservations;')
cur.execute('DELETE FROM rooms;')
cur.execute('DELETE FROM flights;')
cur.execute('DELETE FROM hotels;')
cur.execute('DELETE FROM customers;')
cur.execute('DELETE FROM airports;')

cur.execute('ALTER SEQUENCE airports_id_seq RESTART WITH 1;')
cur.execute('ALTER SEQUENCE hotels_id_seq RESTART WITH 1;')
cur.execute('ALTER SEQUENCE flights_id_seq RESTART WITH 1;')
cur.execute('ALTER SEQUENCE rooms_id_seq RESTART WITH 1;')
cur.execute('ALTER SEQUENCE customers_id_seq RESTART WITH 1;')
cur.execute('ALTER SEQUENCE flight_reservations_id_seq RESTART WITH 1;')
cur.execute('ALTER SEQUENCE hotel_reservations_id_seq RESTART WITH 1;')
cur.execute('ALTER SEQUENCE payments_id_seq RESTART WITH 1;')

conn.commit()

# =========================
# AIRPORTS
# =========================
print('Inserindo aeroportos...')

for airport in AIRPORTS:
    cur.execute(
        '''
        INSERT INTO airports(code, name, city, country)
        VALUES (%s, %s, %s, %s)
        ''',
        airport
    )

conn.commit()

# =========================
# HOTELS
# =========================
print('Inserindo hotéis...')

hotel_ids = []

for _ in range(500):
    cur.execute(
        '''
        INSERT INTO hotels(name, city, country, stars, address)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        ''',
        (
            fake.company() + ' Hotel',
            fake.city(),
            'Brasil',
            random.randint(3, 5),
            fake.address()
        )
    )

    hotel_ids.append(cur.fetchone()[0])

conn.commit()

# =========================
# ROOMS
# =========================
print('Inserindo quartos...')

room_ids = []

for hotel_id in hotel_ids:
    total_rooms = random.randint(20, 80)

    for room_number in range(1, total_rooms + 1):
        room_type = random.choice(HOTEL_TYPES)

        capacity = {
            'single': 1,
            'double': 2,
            'suite': 4
        }[room_type]

        price = {
            'single': random.randint(120, 250),
            'double': random.randint(250, 500),
            'suite': random.randint(500, 1200)
        }[room_type]

        cur.execute(
            '''
            INSERT INTO rooms(
                hotel_id,
                room_number,
                type,
                capacity,
                price_per_night
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            ''',
            (
                hotel_id,
                str(room_number),
                room_type,
                capacity,
                price
            )
        )

        room_ids.append(cur.fetchone()[0])

conn.commit()

# =========================
# CUSTOMERS
# =========================
print('Inserindo clientes...')

customer_ids = []

for _ in range(10000):
    cur.execute(
        '''
        INSERT INTO customers(
            name,
            email,
            cpf,
            phone
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
        ''',
        (
            fake.name(),
            fake.unique.email(),
            fake.unique.cpf(),
            fake.phone_number()
        )
    )

    customer_ids.append(cur.fetchone()[0])

conn.commit()

# =========================
# FLIGHTS
# =========================
print('Inserindo voos...')

flight_ids = []

for i in range(25000):
    origin = random.randint(1, len(AIRPORTS))
    destination = random.randint(1, len(AIRPORTS))

    while destination == origin:
        destination = random.randint(1, len(AIRPORTS))

    departure = datetime.now() + timedelta(
        days=random.randint(-30, 180),
        hours=random.randint(0, 23)
    )

    duration_hours = random.randint(1, 5)
    arrival = departure + timedelta(hours=duration_hours)

    total_seats = random.randint(100, 300)
    reserved = random.randint(0, total_seats - 1)

    cur.execute(
        '''
        INSERT INTO flights(
            flight_number,
            origin_airport_id,
            destination_airport_id,
            departure_time,
            arrival_time,
            total_seats,
            available_seats,
            price
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        ''',
        (
            f'BH{i+1000}',
            origin,
            destination,
            departure,
            arrival,
            total_seats,
            total_seats - reserved,
            round(random.uniform(250, 2500), 2)
        )
    )

    flight_ids.append(cur.fetchone()[0])

conn.commit()

# =========================
# FLIGHT RESERVATIONS
# =========================
print('Inserindo reservas de voo...')

flight_reservation_ids = []

for _ in range(15000):
    status = random.choice(RESERVATION_STATUS)

    cur.execute(
        '''
        INSERT INTO flight_reservations(
            customer_id,
            flight_id,
            seat_number,
            status
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
        ''',
        (
            random.choice(customer_ids),
            random.choice(flight_ids),
            f'{random.randint(1, 40)}{random.choice(["A", "B", "C", "D"])}',
            status
        )
    )

    flight_reservation_ids.append(cur.fetchone()[0])

conn.commit()

# =========================
# HOTEL RESERVATIONS
# =========================
print('Inserindo reservas de hotel...')

hotel_reservation_ids = []

for _ in range(10000):
    check_in = fake.date_between(start_date='-60d', end_date='+120d')
    check_out = check_in + timedelta(days=random.randint(1, 10))

    total_price = round(random.uniform(300, 5000), 2)

    cur.execute(
        '''
        INSERT INTO hotel_reservations(
            customer_id,
            room_id,
            check_in,
            check_out,
            status,
            total_price
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        ''',
        (
            random.choice(customer_ids),
            random.choice(room_ids),
            check_in,
            check_out,
            random.choice(RESERVATION_STATUS),
            total_price
        )
    )

    hotel_reservation_ids.append(cur.fetchone()[0])

conn.commit()

# =========================
# PAYMENTS
# =========================
print('Inserindo pagamentos...')

for _ in range(20000):
    reservation_type = random.choice(['flight', 'hotel'])

    if reservation_type == 'flight':
        reservation_id = random.choice(flight_reservation_ids)
    else:
        reservation_id = random.choice(hotel_reservation_ids)

    cur.execute(
        '''
        INSERT INTO payments(
            reservation_type,
            reservation_id,
            amount,
            status,
            payment_method
        )
        VALUES (%s, %s, %s, %s, %s)
        ''',
        (
            reservation_type,
            reservation_id,
            round(random.uniform(100, 5000), 2),
            random.choice(PAYMENT_STATUS),
            random.choice(PAYMENT_METHODS)
        )
    )

conn.commit()

# =========================
# FINALIZAÇÃO
# =========================
cur.close()
conn.close()

print('\nBanco populado com sucesso!')