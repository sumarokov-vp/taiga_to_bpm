-- Purpose: This script is used to update the task done date when the status is changed to done.
CREATE OR REPLACE FUNCTION public.task_before ()
	RETURNS TRIGGER
	LANGUAGE plpgsql
	AS $$
DECLARE
	done_status int4;
BEGIN
	SELECT
		done_status_id INTO done_status
	FROM
		bpm_project_settings
	WHERE
		project_id = NEW.project_id;
	IF NEW.status_id = done_status AND NEW.status_id != OLD.status_id THEN
		SELECT
			done_status_id INTO done_status
		FROM
			bpm_project_settings
		WHERE
			project_id = NEW.project_id;

		UPDATE
			custom_attributes_taskcustomattributesvalues v
		SET
			attributes_values = attributes_values || jsonb_build_object (s.done_date_id::VARCHAR,
				now()::DATE::VARCHAR)
		FROM
			tasks_task t,
			bpm_project_settings s
		WHERE
			v.task_id = NEW.id
			AND t.id = v.task_id
			AND s.project_id = t.project_id;
	END IF;
	RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER before_insert BEFORE INSERT ON public.tasks_task FOR EACH ROW EXECUTE FUNCTION public.task_before ();
CREATE OR REPLACE TRIGGER before_update BEFORE UPDATE ON public.tasks_task FOR EACH ROW EXECUTE FUNCTION public.task_before ();
