# Standard Library
import logging
import os
import signal
import sys

# Third Party Stuff
from dotenv import load_dotenv

# My Stuff
# Local Application
from notification_listener.listener import (
    PostgresNotificationListener,
)
from notification_listener.processor import (
    DefaultNotificationProcessor,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("notification_listener")


def main() -> None:
    """Main entry point for notification listener service"""
    load_dotenv()

    # Get database URL from environment
    db_url = os.environ.get("DB_URL")
    if not db_url:
        logger.error("DB_URL environment variable not set")
        sys.exit(1)

    # Initialize processor and listener
    processor = DefaultNotificationProcessor(logger)
    listener = PostgresNotificationListener(
        db_url=db_url,
        processor=processor,
        logger=logger,
    )

    # Set up signal handling for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received, stopping listener")
        listener.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the listener
    try:
        listener.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping listener")
        listener.stop()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        listener.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
