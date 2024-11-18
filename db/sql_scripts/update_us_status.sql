CREATE OR REPLACE FUNCTION update_us_status(task_id INT)
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
    WHERE   id = task_id;

    WITH task_statuses AS (
    -- Подзапрос для получения статусов всех задач, связанных с конкретной историей (id = 254)
    SELECT 
        t.user_story_id,
        bool_and(t.status_id = ps.task_finished_status_id) AS all_tasks_finished,
        bool_and(t.status_id = ps.estimated_status_id) AS all_tasks_estimated,
        bool_or(t.status_id = ps.task_need_estimate_status_id) AS any_tasks_need_estimate
    FROM public.tasks_task t
    JOIN public.bpm_project_settings ps ON t.project_id = ps.project_id
    WHERE t.user_story_id = us_id  -- Фильтр по конкретной истории
    GROUP BY t.user_story_id
    )

    -- Основной запрос для обновления статуса только для конкретной истории с id = 254
    UPDATE public.userstories_userstory
    SET status_id = CASE
    -- История в спринте
    WHEN milestone_id IS NOT NULL THEN
        CASE
            WHEN ts.all_tasks_finished THEN ps.story_finished_status_id
            ELSE ps.story_inprocess_status_id
        END
    -- История не в спринте
    ELSE
        CASE
            WHEN ts.all_tasks_estimated THEN ps.story_estimated_status_id
            WHEN ts.any_tasks_need_estimate THEN ps.us_need_estimate_status_id
            ELSE ps.story_preparint_status_id
        END
    END
    FROM task_statuses ts, public.bpm_project_settings ps
    WHERE public.userstories_userstory.id = ts.user_story_id
        AND public.userstories_userstory.status_id != ps.us_income_status_id
        AND public.userstories_userstory.project_id = ps.project_id
        AND public.userstories_userstory.id = us_id;
END;
$function$;
