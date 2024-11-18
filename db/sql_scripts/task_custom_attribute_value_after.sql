CREATE OR REPLACE FUNCTION public.task_custom_attribute_value_after()
RETURNS trigger
LANGUAGE plpgsql
AS
$function$
DECLARE
	us_id int;
	estimate_hours numeric;
	estimated_status int;
	current_status int;
	project_task_default_status int;
BEGIN
	SELECT
		user_story_id INTO us_id
	FROM
		tasks_task
	WHERE
		id = NEW.task_id;
	SELECT
		estimate INTO estimate_hours
	FROM
		bpm_tasks_hours
	WHERE
		id = NEW.task_id;
	SELECT
		estimated_status_id INTO estimated_status
	FROM
		bpm_project_settings
		JOIN tasks_task t ON t.project_id = bpm_project_settings.project_id
	WHERE
		t.id = NEW.task_id;
	SELECT
		status_id INTO current_status
	FROM
		tasks_task
	WHERE
		id = NEW.task_id;
	SELECT
		default_task_status_id INTO project_task_default_status
	FROM
		projects_project
		JOIN tasks_task t ON t.project_id = projects_project.id
	WHERE
		t.id = NEW.task_id;

  -- Set task status to estimated status if estimate is greater than 0 and task status is default project status
	IF estimate_hours > 0 AND current_status = project_task_default_status THEN
		UPDATE
			tasks_task
		SET
			status_id = estimated_status
		WHERE
			id = NEW.task_id;
	END IF;

	-- User story actions
	IF us_id IS NOT NULL THEN
		-- update user story
        PERFORM update_us_estimate_total(NEW.task_id);
        PERFORM update_us_estimate_not_finished(NEW.task_id);
        PERFORM update_us_tracked_total(NEW.task_id);
	END IF;
	RETURN NEW;
END;
$function$;

CREATE OR REPLACE TRIGGER after_insert AFTER INSERT ON public.custom_attributes_taskcustomattributesvalues FOR EACH ROW EXECUTE FUNCTION public.task_custom_attribute_value_after();
CREATE OR REPLACE TRIGGER after_update AFTER UPDATE ON public.custom_attributes_taskcustomattributesvalues FOR EACH ROW EXECUTE FUNCTION public.task_custom_attribute_value_after();
