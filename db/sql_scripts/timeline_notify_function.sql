CREATE OR REPLACE FUNCTION timeline_notify_function()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('taiga_timeline_channel', 
        json_build_object(
            'id', NEW.id,
            'event_type', NEW.event_type,
            'data', NEW.data,
            'created', NEW.created,
            'project_id', NEW.project_id
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;