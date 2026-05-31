CREATE TABLE airports (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100)
);

CREATE TABLE hotels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    stars INT,
    address TEXT
);

CREATE TABLE flights (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(20) UNIQUE NOT NULL,
    origin_airport_id INT REFERENCES airports(id),
    destination_airport_id INT REFERENCES airports(id),
    departure_time TIMESTAMP NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    total_seats INT NOT NULL,
    available_seats INT NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    hotel_id INT REFERENCES hotels(id),
    room_number VARCHAR(20),
    type VARCHAR(20),
    capacity INT,
    price_per_night NUMERIC(10,2)
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    cpf VARCHAR(20) UNIQUE,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE flight_reservations (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    flight_id INT REFERENCES flights(id),
    seat_number VARCHAR(10),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hotel_reservations (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    room_id INT REFERENCES rooms(id),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status VARCHAR(20),
    total_price NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    reservation_type VARCHAR(20),
    reservation_id INT,
    amount NUMERIC(10,2),
    status VARCHAR(20),
    payment_method VARCHAR(50),
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);