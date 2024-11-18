create or replace function public.task_after()
returns trigger
language plpgsql
as
    $function$
DECLARE
	estimated_status int4;
BEGIN

	IF NEW.user_story_id IS NOT NULL THEN
		-- update user story estimate total
        PERFORM update_us_estimate_total(NEW.id);
        PERFORM update_us_estimate_not_finished(NEW.id);
        PERFORM update_us_tracked_total(NEW.id);
        PERFORM update_us_status(NEW.id);
            
	END IF;

  RETURN NEW;
END;
$function$
;

CREATE OR REPLACE TRIGGER after_insert AFTER INSERT ON public.tasks_task FOR EACH ROW EXECUTE FUNCTION public.task_after ();
CREATE OR REPLACE TRIGGER after_update AFTER UPDATE ON public.tasks_task FOR EACH ROW EXECUTE FUNCTION public.task_after ();
