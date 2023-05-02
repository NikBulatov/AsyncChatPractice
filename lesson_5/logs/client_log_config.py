import os
import logging
import sys

sys.path.append("../")

FORMATTER = logging.Formatter('%(levelname)s %(asctime)s %(filename)s %(message)s')

LOG_PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(LOG_PATH, "client.log")

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

LOG_FILE = logging.FileHandler(PATH, encoding="utf8")
LOG_FILE.setFormatter(FORMATTER)

CLIENT_LOGGER = logging.getLogger("client")
CLIENT_LOGGER.addHandler(STREAM_HANDLER)
CLIENT_LOGGER.addHandler(LOG_FILE)
CLIENT_LOGGER.setLevel(logging.DEBUG)

if __name__ == "__main__":
    CLIENT_LOGGER.critical("Critical error")
    CLIENT_LOGGER.error("Error")
    CLIENT_LOGGER.debug("Debug info!")
    CLIENT_LOGGER.info("FYI")
