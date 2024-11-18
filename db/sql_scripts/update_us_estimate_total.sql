CREATE OR REPLACE FUNCTION update_us_estimate_total(task_id INT)
RETURNS VOID
LANGUAGE plpgsql
AS $function$
DECLARE
	us_id int;
BEGIN
  SELECT
    user_story_id INTO us_id
  FROM
    tasks_task
  WHERE
    id = task_id;

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
      t.id = task_id
      AND v.user_story_id = t.user_story_id
      AND s.project_id = t.project_id;
END;
$function$;
