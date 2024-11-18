CREATE OR REPLACE VIEW bpm_us_hours_02 AS
SELECT
    userstory.id,
    userstory.milestone_id,
    Replace(Replace(
        Coalesce(
            (
                attr.attributes_values::json
                -> fields.us_estimate_not_finished_id::varchar
            )::varchar, '0'
        ), 'null', '0'
    ), '"', '')
    ::numeric
    AS not_finished_estimated,

    Replace(Replace(
        Coalesce(
            (
                attr.attributes_values::json
                -> fields.us_tracked_total_id::varchar
            )::varchar, '0'
        ), 'null', '0'
    ), '"', '')
    ::numeric
    AS total_tracked,

    Replace(Replace(
        Coalesce(
            (
                attr.attributes_values::json
                -> fields.us_estimate_total_id::varchar
            )::varchar, '0'
        ), 'null', '0'
    ), '"', '')
    ::numeric
    AS total_estimated

FROM
    userstories_userstory AS userstory
LEFT JOIN custom_attributes_userstorycustomattributesvalues AS attr
    ON attr.user_story_id = userstory.id
LEFT JOIN
    bpm_project_settings AS fields
    ON fields.project_id = userstory.project_id

;
