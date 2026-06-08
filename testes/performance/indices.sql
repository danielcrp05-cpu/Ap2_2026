-- voos_disponiveis_filtro
CREATE INDEX idx_flight_reservations_customer ON flight_reservations (customer_id, flight_id, id, status);
CREATE INDEX idx_payments_reservation ON payments (reservation_id, reservation_type, amount);
CREATE INDEX idx_hotel_reservations_customer ON hotel_reservations (customer_id, room_id, id, status, check_in);
CREATE INDEX idx_rooms_hotel ON rooms (id, hotel_id);

-- taxa_ocupacao_voo
CREATE INDEX idx_rooms_hotel ON rooms (hotel_id, id, room_number, type, price_per_night);
CREATE INDEX idx_hotel_reservations_availability ON hotel_reservations (room_id, status, check_in, check_out);

-- quartos_disponiveis_sem_conflito
CREATE INDEX idx_flights_departure ON flights (departure_time, id, flight_number, total_seats);
CREATE INDEX idx_flight_reservations_confirmed ON flight_reservations (flight_id, status, id);
CREATE INDEX idx_fr_confirmed_partial ON flight_reservations (flight_id, id)
WHERE status = 'confirmed';

-- historico_completo_cliente
CREATE INDEX idx_airports_city ON airports (city, id, code);
CREATE INDEX idx_flights_route_date ON flights (
    origin_airport_id,
    destination_airport_id,
    departure_time,
    available_seats
)
WHERE available_seats > 0