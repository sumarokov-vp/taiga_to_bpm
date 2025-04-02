# Standard Library
import logging
import os
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

# Third Party Stuff
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

# My Stuff
# Local Application
from notification_listener.interfaces import IDataStorage


class PostgresDataStorage(IDataStorage):
    """PostgreSQL implementation of data storage"""

    def __init__(self, db_url: str) -> None:
        """Initialize with database URL

        Args:
            db_url: PostgreSQL connection string
        """
        self.db_url = db_url
        self.logger = logging.getLogger("postgres_storage")

    def get_users_by_role_id(self, role_id: int) -> List[Dict[str, Any]]:
        """Get users with specific role

        Args:
            role_id: Role identifier

        Returns:
            List of user records with telegram_id
        """
        query = """
        SELECT u.id, u.telegram_id, u.name, u.full_name
        FROM bot_users u
        JOIN bot_user_roles ur ON ur.user_id = u.id
        JOIN bot_roles r ON r.id = ur.role_id
        WHERE r.id = %(role_id)s
        """
        args = {"role_id": role_id}

        return self.get_all(query, args)

    def get_taiga_user_by_id(self, user_id: int) -> Dict[str, Any] | None:
        """Get Taiga user by their id

        Args:
            user_id: Taiga user identifier

        Returns:
            User record or None if not found
        """
        query = """
        SELECT u.id, u.username, u.full_name, u.username as name, b.telegram_id
        FROM users_user u
        LEFT JOIN bot_users b ON b.taiga_id = u.id
        WHERE u.id = %(user_id)s
        """
        args = {"user_id": user_id}

        return self.get_one(query, args)

    def execute_query(self, query: str, args: Optional[Dict[str, Any]] = None) -> None:
        """Execute a query without returning results

        Args:
            query: SQL query to execute
            args: Query parameters
        """
        try:
            with connect(conninfo=self.db_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, args)
                    conn.commit()
        except Exception as e:
            self.logger.error(f"Database error: {str(e)}")
            raise

    def get_one(
        self, query: str, args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any] | None:
        """Get a single record from database

        Args:
            query: SQL query to execute
            args: Query parameters

        Returns:
            Single record or None if not found
        """
        try:
            with connect(conninfo=self.db_url, row_factory=dict_row) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, args)
                    return cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Database error: {str(e)}")
            return None

    def get_all(
        self, query: str, args: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get multiple records from database

        Args:
            query: SQL query to execute
            args: Query parameters

        Returns:
            List of records
        """
        try:
            with connect(conninfo=self.db_url, row_factory=dict_row) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, args)
                    return cursor.fetchall() or []
        except Exception as e:
            self.logger.error(f"Database error: {str(e)}")
            return []


# Singleton factory function for creating data storage
def get_data_storage() -> IDataStorage:
    """Create data storage instance

    Returns:
        Data storage implementation
    """
    load_dotenv()
    db_url = os.environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")

    return PostgresDataStorage(db_url)
