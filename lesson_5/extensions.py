import json
from socket import socket

# Variables
DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = "127.0.0.1"
MAX_CONNECTIONS = 2
MAX_PACKAGE_LENGTH = 4096
ENCODING = "utf-8"

ACTION = "action"
TIME = "time"
USER = "user"
ACCOUNT_NAME = "name"

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'


# actions
def get_message(client: socket):
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock: socket, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
