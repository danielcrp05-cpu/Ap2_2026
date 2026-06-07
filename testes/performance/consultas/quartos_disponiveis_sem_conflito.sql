SELECT
    r.id,
    r.room_number,
    r.type,
    r.price_per_night
FROM
    rooms r
WHERE
    r.hotel_id = :hotel_id
    AND r.id NOT IN (
        SELECT
            hr.room_id
        FROM
            hotel_reservations hr
        WHERE
            hr.status != 'cancelled'
            AND hr.check_in < :check_out
            AND hr.check_out > :check_in
    );