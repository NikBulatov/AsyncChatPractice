import json
import socket
import time
import inspect
import sys
import logging
from builtins import callable
from functools import wraps
from .errors import (NonDictionaryInputError, ServerError,
                     IncorrectDataReceivedError)
from .variables import (ACTION, ACCOUNT_NAME, RESPONSE,
                        PRESENCE, TIME, USER, ERROR, ENCODING,
                        MAX_PACKAGE_LENGTH, MESSAGE,
                        MESSAGE_TEXT, SENDER)


def get_logger():
    if sys.argv[0].find("client") == -1:
        logger = logging.getLogger("server")
    else:
        logger = logging.getLogger("client")
    return logger


# if sys.argv[0].find("client") == -1:
#     LOGGER = logging.getLogger("server")
# else:
#     LOGGER = logging.getLogger("client")


LOGGER = get_logger()


def log(func: callable) -> callable:
    """
    Decorator for logging when and where decorated function was called
    :param func: callable
    :return: callable
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        LOGGER.debug(
            f"\"{func.__name__}\" function with arguments {args}, {kwargs} "
            f"was called from \"{inspect.stack()[1][3]}\" function, "
            f"from module {func.__module__}")
        return result

    return wrapper


@log
def create_message(sock: socket, account_name: str = 'Guest') -> dict:
    """
    The function requests the message text and returns it.
    It also closes script when user enter a similar command.
    :param sock: socket
    :param account_name: str
    :return:
    """
    message = input("Input message. Input 'q' to stop command:\n\r")
    if message == 'q':
        sock.close()
        LOGGER.info("Completion of work on the user's command.")
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: MESSAGE_TEXT
    }
    LOGGER.debug(f'Message created: {message_dict}')
    return message_dict


@log
def create_presence(account_name: str = "Guest") -> dict:
    """
    Function to create a presence message with the given account name

    :param account_name: str
    :return: dict
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(f"Message:{PRESENCE} is ready for user: {account_name}")
    return out


@log
def process_client_message(message: dict, messages: list,
                           client: socket) -> None:
    """
    Handler of messages from clients, receives message from the client,
    validate it, sends a dictionary response to the client.

    :param message: dict
    :param messages: list
    :param client: socket
    """
    LOGGER.debug(f"Parse client message {message}")
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == "Guest":
        send_message(client, {RESPONSE: 200})
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
            and MESSAGE_TEXT in message:
        messages.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
    else:
        send_message(client, {RESPONSE: 400, ERROR: "Bad Request"})


@log
def get_message(client: socket) -> dict:
    """
    A function for receiving and decoding a message, accepts bytes,
    returns a dictionary or raise an exception due to an error value

    :param client: socket
    :return: dict
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataReceivedError
    raise IncorrectDataReceivedError


@log
def send_message(sock: socket, message: dict) -> None:
    """
    The function of encoding and sending a message,
    it takes a dictionary and sends it.

    :param sock: socket
    :param message:
    :return:
    """
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)


@log
def process_server_response(message: dict) -> str:
    """
    The function parses the server's response to the presence message,
    returns 200 if everything is OK, or raise an exception due to errors

    :param message: dict
    :return: str
    """
    LOGGER.debug(f"Parse server message: {message}")
    if isinstance(message, dict):
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return "200 : OK"
            raise ServerError(f"400 : {message[ERROR]}")
    raise NonDictionaryInputError


@log
def message_from_server(message: dict) -> None:
    """
    Handler of messages from other users coming from the server
    :param message: dict
    :return:
    """
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f"Received message from user "
              f"{message[SENDER]}:\n{message[MESSAGE_TEXT]}")
        LOGGER.info(f"Received message from user "
                    f"{message[SENDER]}:\n{message[MESSAGE_TEXT]}")
    else:
        LOGGER.error(f"Received incorrect message from server: {message}")
