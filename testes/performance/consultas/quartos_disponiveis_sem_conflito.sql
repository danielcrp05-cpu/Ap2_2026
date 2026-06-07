SELECT
    r.id,
    r.room_number,
    r.type,
    r.price_per_night
FROM
    rooms r
WHERE
    r.hotel_id = 2
    AND r.id NOT IN (
        SELECT
            hr.room_id
        FROM
            hotel_reservations hr
        WHERE
            hr.status != 'cancelled'
            AND hr.check_in < '2026-12-25'
            AND hr.check_out > '2026-12-26'
    );