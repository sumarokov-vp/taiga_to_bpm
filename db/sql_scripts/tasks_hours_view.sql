BEGIN;
DROP VIEW IF EXISTS bpm_tasks_hours;


CREATE OR REPLACE VIEW bpm_tasks_hours AS
SELECT
    task.id,
	ROUND(REPLACE(COALESCE((attr.attributes_values::json -> fields.tracked_hours_id::varchar)::varchar, '0'), 'null', '0')::NUMERIC + REPLACE(COALESCE((attr.attributes_values::json -> fields.tracked_minutes_id::varchar)::varchar, '0'), 'null', '0')::NUMERIC / 60, 2) AS hours,
	u.full_name AS assignee,
	(attr.attributes_values::json -> fields.done_date_id::text)::text::DATE AS done_date,
	task.user_story_id,
	REPLACE(COALESCE((attr.attributes_values::json -> fields.estimate_id::varchar)::varchar, '0'), 'null', '0')::NUMERIC AS estimate,
  'https://taiga.smartist.dev/project/'|| projects_project.slug ||'/task/' || task.ref::text AS url
FROM
	tasks_task AS task
	LEFT JOIN custom_attributes_taskcustomattributesvalues AS attr ON attr.task_id = task.id
	LEFT JOIN bpm_project_settings AS fields ON fields.project_id = task.project_id
	LEFT JOIN users_user u ON u.id = assigned_to_id
	LEFT JOIN projects_project ON task.project_id = projects_project.id
	ORDER BY done_date DESC, assignee
;
COMMIT;
