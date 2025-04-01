-- Создаем триггер для таблицы timeline_timeline с фильтром по content_type_id=15
CREATE TRIGGER timeline_notify_trigger
AFTER INSERT ON timeline_timeline
FOR EACH ROW
WHEN (NEW.content_type_id = 15)
EXECUTE FUNCTION timeline_notify_function();