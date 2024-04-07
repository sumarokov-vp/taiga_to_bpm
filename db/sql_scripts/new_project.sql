create or replace function public.new_project(new_project_id int4)

returns void
language plpgsql
as
    $function$
DECLARE
	estimate int4;
  tracked_hours int4;
  tracked_minutes int4;
  done_date int4;

  task_need_estimate_status int4;
  topay_status int4;
  done_status int4;
  estimated_status int4;
  task_finished_status int4;

  story_income_status int4;
  story_preparint_status int4;
  story_estimated_status int4;
  story_inprocess_status int4;
  story_finished_status int4;
BEGIN
  IF (select count(*) from bpm_project_settings ps where ps.project_id = $1) > 0 THEN
    RAISE EXCEPTION 'Project already exists';
  END IF;
  UPDATE projects_project SET default_task_status_id = NULL WHERE id = $1;
  UPDATE projects_project SET default_us_status_id = NULL WHERE id = $1;

  --- Custom attributes
  DELETE FROM custom_attributes_taskcustomattribute WHERE project_id = $1;

  INSERT INTO custom_attributes_taskcustomattribute
    (project_id, "name", description, "order", created_date, modified_date, type)
  VALUES
    ($1,'Estimate', 'Estimate', 1, now(), now(), 'number')
  RETURNING id INTO estimate;

  INSERT INTO custom_attributes_taskcustomattribute
    (project_id, "name", description, "order", created_date, modified_date, type)
  VALUES
    ($1,'Tracked Hours', 'Tracked Hours', 2, now(), now(), 'number')
    RETURNING id INTO tracked_hours;

  INSERT INTO custom_attributes_taskcustomattribute
  (project_id, "name", description, "order", created_date, modified_date, type)
  VALUES
  ($1,'Tracked Minutes', 'Tracked Minutes', 3, now(), now(), 'number')
  RETURNING id INTO tracked_minutes;

  INSERT INTO custom_attributes_taskcustomattribute
  (project_id, "name", description, "order", created_date, modified_date, type)
  VALUES
  ($1,'Done date', 'Done date', 4, now(), now(), 'date')
  RETURNING id INTO done_date;

  --- Task statuses
  DELETE FROM projects_taskstatus WHERE project_id = $1;

  INSERT INTO projects_taskstatus
    (project_id, "name", "order", is_closed, color, slug)
    VALUES
      ($1, 'Need estimate', 1, false, '#E44057', 'need-estimate')
      RETURNING id INTO task_need_estimate_status;

  UPDATE projects_project SET default_task_status_id = task_need_estimate_status WHERE id = $1;

  INSERT INTO projects_taskstatus
    (project_id, "name", "order", is_closed, color, slug)
    VALUES
      ($1, 'Estimated', 2, false, '#A9AABC', 'estimated')
      RETURNING id INTO estimated_status;

  INSERT INTO projects_taskstatus
    (project_id, "name", "order", is_closed, color, slug)
    VALUES
      ($1, 'To Do', 3, false, '#78D351', 'to-do');

  INSERT INTO projects_taskstatus
    (project_id, "name", "order", is_closed, color, slug)
    VALUES
      ($1, 'In progress', 4, false, '#70728F', 'in-progress');

  INSERT INTO projects_taskstatus
    (project_id, "name", "order", is_closed, color, slug)
    VALUES
      ($1, 'Ready for test (done)', 5, false, '#70728F', 'ready-for-test-done')
      RETURNING id INTO done_status;

  INSERT INTO projects_taskstatus
    (project_id, "name", "order", is_closed, color, slug)
    VALUES
      ($1, 'Tested', 6, false, '#70728F', 'tested');

  INSERT INTO projects_taskstatus
    (project_id, "name", "order", is_closed, color, slug)
    VALUES
      ($1, 'To pay', 7, false, '#A9AABC', 'to-pay')
      RETURNING id INTO topay_status;

  INSERT INTO projects_taskstatus
    (project_id, "name", "order", is_closed, color, slug)
    VALUES
      ($1, 'Paid', 8, false, '#A9AABC', 'paid')
      RETURNING id INTO task_finished_status;

  --- Story statuses
  DELETE FROM projects_userstorystatus WHERE project_id = $1;

  INSERT INTO projects_userstorystatus
    (project_id, "name", "order", is_closed, is_archived, color, slug)
    VALUES
      ($1, 'Income', 1, false, false, '#70728F', 'income')
      RETURNING id INTO story_income_status;
  UPDATE projects_project SET default_us_status_id = story_income_status WHERE id = $1;

  INSERT INTO projects_userstorystatus
    (project_id, "name", "order", is_closed, is_archived, color, slug)
    VALUES
      ($1, 'Preparing', 2, false, false, '#E44057', 'preparing')
      RETURNING id INTO story_preparint_status;

  INSERT INTO projects_userstorystatus
  (project_id, "name", "order", is_closed, is_archived, color, slug)
  VALUES
    ($1, 'Need estimate', 3, false, false, '#E44057', 'need-estimate');

  INSERT INTO projects_userstorystatus
  (project_id, "name", "order", is_closed, is_archived, color, slug)
  VALUES
    ($1, 'Estimated', 4, false, false, '#E47C40', 'estimated')
    RETURNING id INTO story_estimated_status;

  INSERT INTO projects_userstorystatus
  (project_id, "name", "order", is_closed, is_archived, color, slug)
  VALUES
    ($1, 'In process', 5, false, false, '#70728F', 'in-process')
    RETURNING id INTO story_inprocess_status;

  INSERT INTO projects_userstorystatus
  (project_id, "name", "order", is_closed, is_archived, color, slug)
  VALUES
    ($1, 'Finished', 6, true, false, '#51D355', 'finished')
    RETURNING id INTO story_finished_status;

  INSERT INTO projects_userstorystatus
  (project_id, "name", "order", is_closed, is_archived, color, slug)
  VALUES
    ($1, 'Archived', 7, true, true, '#70728F', 'archived');

  -- Project settings
  INSERT INTO bpm_project_settings
    (
      project_id,

      -- Custom attributes
      estimate_id,
      tracked_hours_id,
      tracked_minutes_id,
      done_date_id,

      -- Task statuses
      topay_status_id,
      done_status_id,
      estimated_status_id,
      task_finished_status_id,

      -- Story statuses
      story_estimated_status_id,
      story_preparint_status_id,
      story_inprocess_status_id,
      story_finished_status_id
    )
    VALUES
    (
      $1,
      estimate,
      tracked_hours,
      tracked_minutes,
      done_date,
      topay_status,
      done_status,
      estimated_status,
      task_finished_status,
      story_estimated_status,
      story_preparint_status,
      story_inprocess_status,
      story_finished_status
    );

 


END;
$function$
;

