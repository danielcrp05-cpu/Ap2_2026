SELECT r.id, r.room_number, r.type, r.price_per_night
FROM rooms r
WHERE r.hotel_id = 284
AND NOT EXISTS (
    SELECT 1
    FROM hotel_reservations hr
    WHERE hr.room_id = r.id
    AND hr.status != 'cancelled'
    AND hr.check_in  < '2026-08-10'
    AND hr.check_out > '2026-09-14'
);