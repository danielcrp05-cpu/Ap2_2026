SELECT
    f.flight_number,
    COUNT(fr.id) AS total_reservas,
    f.total_seats,
    ROUND(COUNT(fr.id) :: numeric / f.total_seats * 100, 2) AS ocupacao_pct
FROM
    flights f
    LEFT JOIN flight_reservations fr ON fr.flight_id = f.id
    AND fr.status = 'confirmed'
WHERE
    f.departure_time >= NOW() - INTERVAL '30 days'
GROUP BY
    f.id,
    f.flight_number,
    f.total_seats
ORDER BY
    ocupacao_pct DESC
LIMIT
    20;