CREATE OR REPLACE FUNCTION update_us_estimate_not_finished(task_id INT)
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
      attributes_values = attributes_values || jsonb_build_object(
          s.us_estimate_not_finished_id::VARCHAR,
          (
              SELECT sum(bpm_tasks_hours.estimate)
              FROM
                  bpm_tasks_hours
                  JOIN  tasks_task t ON t.id = bpm_tasks_hours.id ,
                  bpm_project_settings AS s
              WHERE
                  bpm_tasks_hours.user_story_id = us_id
                  AND s.project_id = t.project_id
                  AND t.status_id NOT IN (
                    s.topay_status_id,
                    s.done_status_id,
                    s.task_finished_status_id,
                    s.task_tested_status_id
                  )
              GROUP BY
                  bpm_tasks_hours.user_story_id
          )::VARCHAR
      )
  FROM
      tasks_task AS t,
      bpm_project_settings AS s
  WHERE
      t.id = task_id
      AND v.user_story_id = t.user_story_id
      AND s.project_id = t.project_id;

END;
$function$;
