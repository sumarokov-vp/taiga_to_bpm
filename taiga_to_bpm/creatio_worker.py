from __future__ import annotations

# Standard Library
from dataclasses import dataclass
from os import environ
from typing import (
    List,
    Optional,
)

# Third Party Stuff
from psycopg import connect
from psycopg.rows import TupleRow

# My Stuff
from db.db_worker import execute_query

from .creatio import Creatio
from .creatio_constants import ODATA_version


def create_receipt(project_id: int) -> Receipt:
    """
    Create receipt in Creatio with tasks from Taiga
    return: receipt_id
    """

    tasks = get_tasks(project_id)

    receipt = Receipt.new(tasks[0].desk_guid)

    print(receipt)
    return receipt


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


def creatio_connection() -> Creatio:
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
    return Creatio(
        creatio_host=bpm_settings[0],
        login=bpm_settings[1],
        password=bpm_settings[2],
        odata_version=api_version,
    )


@dataclass
class Receipt:
    guid: str
    url: str

    @classmethod
    def new(cls, desk_guid: str) -> Receipt:
        creatio = creatio_connection()
        dict_data = {"SLTrelloDeskId": desk_guid}
        print(f"Creating receipt: {dict_data=}")
        receipt_odata_dict = creatio.create_object("SLReceipt", dict_data)
        if not receipt_odata_dict:
            raise ValueError("Receipt not created")
        try:
            error = receipt_odata_dict["error"]
            raise ValueError(
                f"Error creating receipt: {error}\n"
                f"Sent data: {dict_data}\n"
                f"Response: {receipt_odata_dict}"
            )
        except KeyError:
            pass
        receipt_id = str(receipt_odata_dict["Id"])
        return cls(
            guid=receipt_id,
            url=(
                f"{creatio.creatio_url}/Nui/ViewModule.aspx#CardModuleV2"
                f"/SLReceipt1Page/edit/{receipt_id}"
            ),
        )

    @classmethod
    def get_from_url(cls, url: str) -> Receipt:
        receipt_id = url.split("/")[-1]
        return cls(
            guid=receipt_id,
            url=url,
        )

    def delete(self, db_url) -> None:
        """
        Use this method to rollback receipt
        only if you have access to Creatio database
        """
        args = {"receipt_id": self.guid}
        query = """
            DELETE FROM public."SLReceiptTask"
            WHERE "SLReceiptId" = %(receipt_id)s
        """
        execute_query(query, args, db_url=db_url)

        # delete receipt
        query = """
            DELETE FROM public."SLReceipt"
            WHERE "Id" = %(receipt_id)s
        """
        execute_query(query, args, db_url=db_url)


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
    url: str
    user_full_name: str
    project_id: Optional[int] = None
    guid: Optional[str] = None

    def push_to_creatio(self, receipt_id: str) -> str:
        """
        return: task_id - guid as string
        """
        if not self.bpm_user_guid:
            raise ValueError(
                f"Task {self.ref} executor not in bpm_users table\n"
                f"Taiga user_id: {self.assigned_to_id}\n"
                f"Taiga user_full_name: {self.user_full_name}\n"
                f"{self.url}"
            )
        minutes_full = self.hours * 60 + self.minutes
        hours = round(minutes_full // 60)
        minutes = round(minutes_full % 60)

        data = {
            "SLName": self.subject,
            "SLExecutorId": self.bpm_user_guid,
            "SLHours": hours,
            "SLMinutes": minutes,
            "SLCardLink": self.url,
            "SLReceiptId": receipt_id,
        }
        creatio = creatio_connection()
        created_task = creatio.create_object(
            object_name="SLReceiptTask",
            data=data,
        )
        if not created_task:
            raise ValueError(f"Task not created: {data=}")
        try:
            error = created_task["error"]
            raise ValueError(f"Error creating task {error}\nSent data: {data}")
        except KeyError:
            pass
        self.guid = created_task["Id"]
        print(f"Created task {self.ref} - {self.guid}")
        assert self.guid
        return self.guid


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
    assigned_to_id, -- 8
    project.slug as project_slug, -- 9
    usr.full_name as user_full_name -- 10
FROM
	tasks_task AS task
	INNER JOIN custom_attributes_taskcustomattributesvalues 
        AS attr ON attr.task_id = task.id
	LEFT JOIN bpm_project_settings AS fields
        ON fields.project_id = task.project_id
	LEFT JOIN bpm_users AS assigned_bpm_user
        ON assigned_bpm_user.user_id = assigned_to_id
    LEFT JOIN projects_project AS project on project.id = task.project_id
    LEFT JOIN users_user AS usr on usr.id = assigned_to_id
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
                        hours=task_row[5] or 0.0,
                        minutes=task_row[6] or 0.0,
                        ref=task_row[7],
                        assigned_to_id=task_row[8],
                        url=f"https://taiga.smartist.dev/project/{task_row[9]}/task/{task_row[7]}",
                        user_full_name=task_row[10],
                    )
                )
            if not tasks or len(tasks) == 0:
                raise ValueError("Tasks not found")
            return tasks
