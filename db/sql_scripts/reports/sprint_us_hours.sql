SELECT
    project.name AS project,
    sprint.name AS sprint,
    sum(bpm_us_hours.total_estimated) AS estimated,
    sum(bpm_us_hours.total_tracked) AS tracked,
    sum(bpm_us_hours.not_finished_estimated) AS not_finished
FROM bpm_us_hours_02 AS bpm_us_hours
INNER JOIN
    milestones_milestone AS sprint
    ON bpm_us_hours.milestone_id = sprint.id
INNER JOIN projects_project AS project ON sprint.project_id = project.id
WHERE sprint.closed = FALSE
GROUP BY project.name, sprint.name, sprint.estimated_start
ORDER BY project.name ASC, sprint.estimated_start DESC;
