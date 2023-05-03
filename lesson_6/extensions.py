import json
from socket import socket

# Variables
DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = "127.0.0.1"
MAX_CONNECTIONS = 2
MAX_PACKAGE_LENGTH = 4096
ENCODING = "utf-8"

# JIM constants
ACTION = "action"
TIME = "time"
USER = "user"
ACCOUNT_NAME = "name"

PRESENCE = "presence"
RESPONSE = "response"
ERROR = "error"


# Actions
def get_message(client: socket) -> dict:
    """
    Function to retrieve a message

    :param client: socket
    :return: dict
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock: socket, message) -> None:
    """
    Function to send a message

    :param sock: socket
    :param message:
    :return:
    """
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
