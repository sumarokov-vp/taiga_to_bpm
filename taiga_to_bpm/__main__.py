# Standard Library
from os import environ

# Third Party Stuff
from dotenv import load_dotenv
from psycopg import connect
from taiga_to_bpm.creatio_worker import create_receipt


def get_project_from_console() -> int:
    db_url = environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM projects_project")
            projects = cursor.fetchall()
            print("Select project (put the number):")
            for project in projects:
                print(f"{project[0]}. {project[1]}")
            return int(input())


if __name__ == "__main__":
    load_dotenv()
    project_id = get_project_from_console()
    print(create_receipt(project_id))
