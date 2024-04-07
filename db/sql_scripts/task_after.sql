CREATE OR REPLACE FUNCTION public.task_after ()
	RETURNS TRIGGER
	LANGUAGE plpgsql
	AS $function$
DECLARE
	estimated_status int4;
BEGIN

  -- if task is not in sprint, update user story status:
  --    if all tasks in user story are estimated, update user story status to estimated
  --    else update user story status to preparing
	UPDATE
		userstories_userstory
	SET
		status_id = (
			SELECT
				coalesce(ps.story_estimated_status_id, ps2.story_preparint_status_id) AS new_story_status
			FROM
				tasks_task t
			LEFT JOIN bpm_project_settings ps ON ps.project_id = t.project_id
				AND t.status_id = ps.estimated_status_id
			JOIN bpm_project_settings ps2 ON ps2.project_id = t.project_id
		WHERE
			t.user_story_id = NEW.user_story_id
		ORDER BY
			ps.story_estimated_status_id DESC
		LIMIT 1)
  WHERE
    userstories_userstory.id = NEW.user_story_id
    AND userstories_userstory.milestone_id is null;


  -- if task is in sprint, update user story status:
  --    if all tasks in user story are finished (paid), update user story status to finished
  --    else update user story status to "in process"
	UPDATE
		userstories_userstory
	SET
		status_id = (
			SELECT
				coalesce(ps.story_finished_status_id, ps2.story_inprocess_status_id) AS new_story_status
			FROM
				tasks_task t
			LEFT JOIN bpm_project_settings ps ON ps.project_id = t.project_id
				AND t.status_id = ps.task_finished_status_id
			JOIN bpm_project_settings ps2 ON ps2.project_id = t.project_id
		WHERE
			t.user_story_id = NEW.user_story_id
		ORDER BY
			ps.story_finished_status_id DESC
		LIMIT 1)
  WHERE
    userstories_userstory.id = NEW.user_story_id
    AND userstories_userstory.milestone_id is not null;

  RETURN NEW;
END;
$function$
;

CREATE OR REPLACE TRIGGER after_insert AFTER INSERT ON public.tasks_task FOR EACH ROW EXECUTE FUNCTION public.task_after ();
CREATE OR REPLACE TRIGGER after_update AFTER UPDATE ON public.tasks_task FOR EACH ROW EXECUTE FUNCTION public.task_after ();
