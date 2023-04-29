import os
import logging.handlers
import logging
import sys

sys.path.append("../")

FORMATTER = logging.Formatter('%(levelname)s %(asctime)s %(filename)s %(message)s')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

LOG_PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(LOG_PATH, "server.log")

LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when="D")
LOG_FILE.setFormatter(FORMATTER)

LOGGER = logging.getLogger("server")
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(LOG_FILE)
LOGGER.addHandler(STREAM_HANDLER)

if __name__ == "__main__":
    LOGGER.critical("Critical error")
    LOGGER.error("Error")
    LOGGER.debug("Debug info!")
    LOGGER.info("FYI")
