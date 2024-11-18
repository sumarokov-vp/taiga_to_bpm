CREATE OR REPLACE VIEW bpm_tasks_hours AS
SELECT
    task.id,
    task.user_story_id,
    u.full_name AS assignee,

    (
        (attr.attributes_values::json -> fields.done_date_id::text)::text
    )::date AS done_date,

    replace(
        coalesce(
            (
                attr.attributes_values::json
                -> fields.estimate_id::character varying::text
            )::character varying,
            '0'::character varying
        )::text,
        'null'::text,
        '0'::text
    )::numeric AS estimate,

    (
        (
            'https://taiga.smartist.dev/project/'::text
            || projects_project.slug::text
        )
        || '/task/'::text
    )
    || task.ref::text AS url,

    round(
        replace(
            coalesce(
                (
                    attr.attributes_values::json
                    -> fields.tracked_hours_id::character varying::text
                )::character varying, '0'::character varying
            )::text, 'null'::text, '0'::text
        )::numeric
        + replace(
            coalesce(
                (
                    attr.attributes_values::json
                    -> fields.tracked_minutes_id::character varying::text
                )::character varying,
                '0'::character varying
            )::text,
            'null'::text,
            '0'::text
        )::numeric
        / 60::numeric,
        2
    ) AS tracked

FROM tasks_task AS task
LEFT JOIN
    custom_attributes_taskcustomattributesvalues AS attr
    ON task.id = attr.task_id
LEFT JOIN bpm_project_settings AS fields ON task.project_id = fields.project_id
LEFT JOIN users_user AS u ON task.assigned_to_id = u.id
LEFT JOIN projects_project ON task.project_id = projects_project.id
ORDER BY
    (((attr.attributes_values::json -> fields.done_date_id::text)::text)::date) DESC,
    u.full_name;
