# Standard Library

# Standard Library
from dataclasses import dataclass
from os import environ
from typing import List

# Third Party Stuff
from psycopg import connect
from psycopg.rows import TupleRow
from sl_creatio_connector.constants import ODATA_version
from sl_creatio_connector.creatio import Creatio


def create_receipt(project_id: int) -> str:
    tasks = get_tasks(project_id)
    if not tasks or len(tasks) == 0:
        return "Таски для закрытия не найдены"
    bpm_settings = get_creatio_settings()[0]
    if not bpm_settings:
        raise ValueError("BPM settings not found")

    api_version_mapping = {
        "v3": ODATA_version.v3,
        "v4": ODATA_version.v4,
        "v4core": ODATA_version.v4core,
    }

    bpm_api_version = bpm_settings[3]
    if bpm_api_version in api_version_mapping:
        api_version = api_version_mapping[bpm_api_version]
    else:
        raise ValueError(f"Unknown API version: {bpm_api_version}")

    creatio = Creatio(
        creatio_host=bpm_settings[0],
        login=bpm_settings[1],
        password=bpm_settings[2],
        odata_version=api_version,
    )
    dict_data = {
        "SLTrelloDeskId": tasks[0].desk_guid,
    }
    print(f"Creating receipt: {dict_data=}")
    receipt = creatio.create_object("SLReceipt", dict_data)
    if not receipt:
        raise ValueError("Receipt not created")

    for task in tasks:
        story_url = f"https://taiga.smartist.dev/project/hapimeets/us/{task.ref}"
        data = {
            "SLName": task.subject,
            "SLExecutorId": task.bpm_user_guid,
            "SLHours": task.hours,
            "SLMinutes": task.minutes,
            "SLCardLink": story_url,
            "SLReceiptId": receipt["Id"],
        }
        creatio_task = creatio.create_object(
            object_name="SLReceiptTask",
            data=data,
        )
        if not creatio_task:
            raise ValueError(f"Task not created: {data=}")
        print(f"Created task: {task.ref} - {creatio_task['Id']}")
    print(
        f"Created receipt: {bpm_settings[0]}/Nui/ViewModule.aspx#CardModuleV2"
        f"/SLReceipt1Page/edit/{receipt['Id']}"
    )
    return "Success"


def get_creatio_settings() -> List[TupleRow]:
    db_url = environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
SELECT
	url_settings.value as url,
	user_settings.value as user,
	pass_settings.value as pass,
	api_settings.value as api_version
FROM
	bpm_settings as url_settings,
	bpm_settings as user_settings,
	bpm_settings as pass_settings,
	bpm_settings as api_settings
WHERE
	url_settings."key" = 'bpm_url'
	AND user_settings."key" = 'bpm_user'
	AND pass_settings."key" = 'bpm_password'
	AND api_settings."key" = 'bpm_version';
                           """
            )
            return cursor.fetchall()


@dataclass
class Task:
    id: int
    subject: str
    bpm_user_guid: str
    desk_guid: str
    estimate: float
    hours: float
    minutes: float
    ref: str
    assigned_to_id: int


def get_tasks(project_id: int) -> List[Task]:
    db_url = environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
SELECT
	task.id, -- 0
	subject, -- 1
	assigned_bpm_user.guid as user_bpm_guid, -- 2
    fields.desk_guid as desk_bpm_guid, -- 3
	attr.attributes_values::json -> fields.estimate_id::text AS estimate, -- 4
	attr.attributes_values::json -> fields.tracked_hours_id::text AS hours, -- 5
	attr.attributes_values::json -> fields.tracked_minutes_id::text AS minutes, -- 6
    task.ref, -- 7
    assigned_to_id -- 8
FROM
	tasks_task AS task
	INNER JOIN custom_attributes_taskcustomattributesvalues 
        AS attr ON attr.task_id = task.id
	LEFT JOIN bpm_project_settings AS fields
        ON fields.project_id = task.project_id
	LEFT JOIN bpm_users AS assigned_bpm_user
        ON assigned_bpm_user.user_id = assigned_to_id
WHERE
	status_id = fields.topay_status_id
    AND task.project_id = %(project_id)s;
""",
                {"project_id": project_id},
            )
            task_rows = cursor.fetchall()
            tasks = []
            for task_row in task_rows:
                tasks.append(
                    Task(
                        id=task_row[0],
                        subject=task_row[1],
                        bpm_user_guid=task_row[2],
                        desk_guid=task_row[3],
                        estimate=task_row[4],
                        hours=task_row[5],
                        minutes=task_row[6],
                        ref=task_row[7],
                        assigned_to_id=task_row[8],
                    )
                )
            return tasks
