import os
import logging
import sys

sys.path.append("../")

FORMATTER = logging.Formatter('%(levelname)s %(asctime)s %(filename)s %(message)s')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

LOG_PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(LOG_PATH, "client.log")

LOG_FILE = logging.FileHandler(PATH, encoding="utf8")
LOG_FILE.setFormatter(FORMATTER)

LOGGER = logging.getLogger("client")
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(LOG_FILE)
LOGGER.addHandler(STREAM_HANDLER)

if __name__ == "__main__":
    LOGGER.critical("Critical error")
    LOGGER.error("Error")
    LOGGER.debug("Debug info!")
    LOGGER.info("FYI")
