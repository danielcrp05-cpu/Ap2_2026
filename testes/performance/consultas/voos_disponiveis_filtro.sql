SELECT
    f.id,
    f.flight_number,
    f.departure_time,
    f.arrival_time,
    f.available_seats,
    f.price,
    a1.code AS origin,
    a2.code AS destination
FROM
    flights f
    JOIN airports a1 ON a1.id = f.origin_airport_id
    JOIN airports a2 ON a2.id = f.destination_airport_id
WHERE
    a1.city = 'São Paulo'
    AND a2.city = 'Rio de Janeiro'
    AND f.departure_time BETWEEN '2026-09-20'
    AND '2026-09-30'
    AND f.available_seats > 0
ORDER BY
    f.departure_time;