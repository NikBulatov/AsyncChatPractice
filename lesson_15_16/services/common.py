import inspect
import logging
import json
import sys
from functools import wraps
from socket import socket

from .errors import IncorrectDataReceivedError, NonDictionaryInputError
from .variables import MAX_PACKAGE_LENGTH, ENCODING, ACTION, PRESENCE


def _get_logger() -> logging.Logger:
    """
    Return client or server logger. It depends by module
    :return:
    """
    if sys.argv[0].find("client") == -1:
        logger = logging.getLogger("server")
    else:
        logger = logging.getLogger("client")
    return logger


LOGGER = _get_logger()


def log(func: callable) -> callable:
    """
    Decorator for logging when and where decorated function was called
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        LOGGER.debug(
            f'"{func.__name__}" function with arguments {args}, {kwargs} '
            f'was called from "{inspect.stack()[1][3]}" function, '
            f"from module {func.__module__}"
        )
        return result

    return wrapper


def login_required(func: callable) -> callable:
    """
    Decorator to check user login
    :param func:
    :return:
    """

    @wraps(func)
    def checker(*args, **kwargs):
        sys.path.append("../")
        from server.core import Server

        if isinstance(args[0], Server):
            found = False
            for arg in args:
                if isinstance(arg, socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker


@log
def get_response(client: socket) -> dict:
    """
    Receive and decode a message. It accepts bytes,
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
def send_request(sock: socket, message: dict) -> None:
    """
    Encode and send a message. It takes a dictionary and sends it.

    :param sock: socket
    :param message:
    :return:
    """
    if not isinstance(message, dict):
        raise NonDictionaryInputError

    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    sock.send(encoded_message)
