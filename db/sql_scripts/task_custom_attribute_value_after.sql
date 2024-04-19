create or replace function public.task_custom_attribute_value_after()
returns trigger
language plpgsql
as
    $function$
DECLARE
	us_id int;
BEGIN
  SELECT
    user_story_id INTO us_id
  FROM
    tasks_task
  WHERE
    id= NEW.task_id;

  -- update user story estimate total
  if us_id is not null then
    UPDATE
      custom_attributes_userstorycustomattributesvalues v
    SET
      attributes_values = attributes_values || jsonb_build_object (s.us_estimate_total_id::VARCHAR,
        (
          SELECT
            sum(estimate)
          FROM
            bpm_tasks_hours h
          WHERE
            user_story_id = us_id
          GROUP BY
            user_story_id)::varchar)
      FROM
        tasks_task t,
        bpm_project_settings s
      WHERE
        t.id = NEW.task_id
        AND v.user_story_id = t.user_story_id
        AND s.project_id = t.project_id;
  end if;

  RETURN NEW;
END;
$function$
;

CREATE OR REPLACE TRIGGER after_insert AFTER INSERT ON public.custom_attributes_taskcustomattributesvalues FOR EACH ROW EXECUTE FUNCTION public.task_custom_attribute_value_after ();
CREATE OR REPLACE TRIGGER after_update AFTER UPDATE ON public.custom_attributes_taskcustomattributesvalues FOR EACH ROW EXECUTE FUNCTION public.task_custom_attribute_value_after ();

