create or replace function public.task_before()
returns trigger
language plpgsql
as $$
DECLARE
	done_status int4;
	in_process_status int4;
BEGIN
	SELECT
		done_status_id,
		ps.task_in_process_status_id
	INTO
		done_status,
		in_process_status
	FROM
		bpm_project_settings ps
	WHERE
		ps.project_id = NEW.project_id;

	IF OLD.status_id != NEW.status_id THEN
		IF OLD.status_id == in_process_status AND NEW.status_id != done_status THEN
			RAISE EXCEPTION 'Task is in progress, you can change status only to done';
		END IF;
	END IF;
	-- Set current date to done_date  when setting done status
	IF NEW.status_id = done_status AND NEW.status_id != OLD.status_id THEN
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
$$
;

CREATE OR REPLACE TRIGGER before_insert BEFORE INSERT ON public.tasks_task FOR EACH ROW EXECUTE FUNCTION public.task_before ();
CREATE OR REPLACE TRIGGER before_update BEFORE UPDATE ON public.tasks_task FOR EACH ROW EXECUTE FUNCTION public.task_before ();

