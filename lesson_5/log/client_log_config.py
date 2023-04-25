import os
import sys
import logging
import logging.handlers

LOGGER = logging.getLogger("client")
LOGGER.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')
LOG_PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(LOG_PATH, "client.log")

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setLevel(logging.ERROR)
STREAM_HANDLER.setFormatter(FORMATTER)

LOG_FILE = logging.FileHandler(PATH, encoding="utf-8")
LOG_FILE.setFormatter(FORMATTER)

LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)

if __name__ == "__main__":
    LOGGER.critical("Critical error")
    LOGGER.error("Error")
    LOGGER.debug("Debug info!")
    LOGGER.info("FYI")
