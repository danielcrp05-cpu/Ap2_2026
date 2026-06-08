SELECT 'DROP INDEX IF EXISTS ' || quote_ident(schemaname) || '.' || quote_ident(indexname) || ' CASCADE;'
FROM pg_indexes
WHERE tablename IN (
    'airports',
    'customers',
    'flight_reservations',
    'flights',
    'hotel_reservations',
    'hotels',
    'payments',
    'rooms'
  )
  AND schemaname = 'public'
  AND NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = indexname
  );