CREATE OR REPLACE FUNCTION notify_new_record_function()
-- comment
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('new_record_channel', 
        json_build_object(
            'id', NEW.id,
            'user_id', NEW.user_id,
            'data', NEW.data,
            'created', NEW.created
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
