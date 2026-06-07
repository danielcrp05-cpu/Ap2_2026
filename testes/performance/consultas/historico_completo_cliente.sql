SELECT 'voo' AS tipo,
    fr.id AS reserva_id,
    f.flight_number AS descricao,
    f.departure_time AS data,
    fr.status,
    p.amount
FROM flight_reservations fr
    JOIN flights f ON f.id = fr.flight_id
    LEFT JOIN payments p ON p.reservation_id = fr.id
    AND p.reservation_type = 'flight'
WHERE fr.customer_id = 9999
UNION ALL
SELECT 'hotel',
    hr.id,
    h.name,
    hr.check_in,
    hr.status,
    p.amount
FROM hotel_reservations hr
    JOIN rooms r ON r.id = hr.room_id
    JOIN hotels h ON h.id = r.hotel_id
    LEFT JOIN payments p ON p.reservation_id = hr.id
    AND p.reservation_type = 'hotel'
WHERE hr.customer_id = 9999
ORDER BY data DESC;