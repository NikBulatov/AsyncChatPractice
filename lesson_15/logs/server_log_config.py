import os
import logging.handlers
import logging
import sys

sys.path.append("../")

FORMATTER = logging.Formatter(
    "%(levelname)s %(asctime)s %(filename)s %(message)s"
)

LOG_PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(LOG_PATH, "server.log")

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

LOG_FILE = logging.handlers.TimedRotatingFileHandler(
    PATH, encoding="utf8", interval=1, when="D"
)
LOG_FILE.setFormatter(FORMATTER)

SERVER_LOGGER = logging.getLogger("server")
SERVER_LOGGER.addHandler(STREAM_HANDLER)
SERVER_LOGGER.addHandler(LOG_FILE)
SERVER_LOGGER.setLevel(logging.DEBUG)

if __name__ == "__main__":
    SERVER_LOGGER.critical("Critical error")
    SERVER_LOGGER.error("Error")
    SERVER_LOGGER.debug("Debug info!")
    SERVER_LOGGER.info("FYI")
