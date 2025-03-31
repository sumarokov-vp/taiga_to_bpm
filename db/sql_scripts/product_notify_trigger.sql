-- 2. Создаем триггер, который будет вызывать эту функцию
CREATE TRIGGER new_record_trigger
AFTER INSERT ON product
FOR EACH ROW
EXECUTE FUNCTION notify_new_record_function();