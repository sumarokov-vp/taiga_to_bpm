-- Удаляем старый триггер с таблицы product
DROP TRIGGER IF EXISTS new_record_trigger ON product;

-- Удаляем старую функцию уведомления
DROP FUNCTION IF EXISTS notify_new_record_function();