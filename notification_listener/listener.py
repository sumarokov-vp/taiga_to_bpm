# Standard Library
import json
import logging
import select
import time
from typing import List, Optional

# Third Party Stuff
import psycopg
from psycopg.sql import SQL, Identifier

# Local Application
from notification_listener.interfaces import (
    INotificationListener,
    IProcessDBNotification,
)


class PostgresNotificationListener(INotificationListener):
    """PostgreSQL notification listener implementation"""

    def __init__(
        self,
        db_url: str,
        processor: IProcessDBNotification,
        channels: List[str] = ["new_record_channel"],
        logger: Optional[logging.Logger] = None,
        reconnect_delay: int = 5,
        poll_timeout: int = 10000,
    ) -> None:
        """Initialize the PostgreSQL notification listener

        Args:
            db_url: PostgreSQL connection URL
            processor: Object implementing IProcessDBNotification interface
            channels: List of notification channels to listen on
            logger: Optional logger instance
            reconnect_delay: Seconds to wait before reconnecting on error
            poll_timeout: Timeout in milliseconds for poll operations
        """
        self.db_url = db_url
        self.processor = processor
        self.channels = channels
        self.logger = logger or logging.getLogger("postgres_listener")
        self.reconnect_delay = reconnect_delay
        self.poll_timeout = poll_timeout
        self.running = False
        self.conn: Optional[psycopg.Connection] = None

    def _connect(self) -> psycopg.Connection:
        """Establish connection to PostgreSQL

        Returns:
            Active PostgreSQL connection
        """
        self.logger.info("Connecting to PostgreSQL database")
        conn = psycopg.connect(conninfo=self.db_url)
        return conn

    def _subscribe_to_channels(self, cursor: psycopg.Cursor) -> None:
        """Subscribe to all notification channels

        Args:
            cursor: Active PostgreSQL cursor
        """
        for channel in self.channels:
            cursor.execute(SQL("LISTEN {};").format(Identifier(channel)))
            self.logger.info(f"Listening on channel: {channel}")

    def _process_notification(self, notification: psycopg.Notify) -> None:
        """Process a single notification

        Args:
            notification: PostgreSQL notification object
        """
        try:
            payload = json.loads(notification.payload)
            self.processor.process(payload)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to decode JSON: {notification.payload}")
        except Exception as e:
            self.logger.error(f"Error processing notification: {str(e)}")

    def start(self) -> None:
        """Start listening for notifications"""
        self.running = True
        self.logger.info("Starting notification listener")

        while self.running:
            try:
                with self._connect() as conn:
                    self.conn = conn
                    with conn.cursor() as cursor:
                        self._subscribe_to_channels(cursor)
                        conn.commit()

                        # Initialize polling object
                        poll = select.poll()
                        poll.register(conn.pgconn.socket, select.POLLIN)

                        # Main listening loop
                        while self.running:
                            if poll.poll(self.poll_timeout):
                                conn.commit()
                                for notification in conn.notifies():
                                    self._process_notification(notification)

                            # Keep-alive query
                            cursor.execute(SQL("SELECT 1"))
                            conn.commit()

            except psycopg.OperationalError as e:
                self.logger.error(f"Database connection error: {str(e)}")
                if self.running:
                    self.logger.info(
                        f"Reconnecting in {self.reconnect_delay} seconds..."
                    )
                    time.sleep(self.reconnect_delay)
            except Exception as e:
                self.logger.error(f"Unexpected error: {str(e)}")
                if self.running:
                    self.logger.info(f"Restarting in {self.reconnect_delay} seconds...")
                    time.sleep(self.reconnect_delay)

    def stop(self) -> None:
        """Stop listening for notifications"""
        self.logger.info("Stopping notification listener")
        self.running = False

        # Close connection if active
        if self.conn and not self.conn.closed:
            self.conn.close()
