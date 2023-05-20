import inspect
import logging
import json
import sys
from functools import wraps
from socket import socket, AF_INET, SOCK_STREAM

from .errors import IncorrectDataReceivedError, NonDictionaryInputError
from .variables import MAX_PACKAGE_LENGTH, ENCODING, MAX_CONNECTIONS


class BaseSocket:

    def __init__(self,
                 timeout: float,
                 max_connections: int):
        self.transport = socket(AF_INET, SOCK_STREAM)
        self.timeout = timeout
        self.max_connections = max_connections

    def _start(self, listen_socket: tuple):
        self.transport.bind(listen_socket)
        self.transport.settimeout(0.5)
        self.transport.listen(MAX_CONNECTIONS)
        return self.transport

    def log(self, func: callable) -> callable:
        """
        Decorator for logging when and where decorated function was called
        :param func: callable
        :return: callable
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            self.LOGGER.debug(
                f"\"{func.__name__}\" function with arguments {args}, {kwargs} "
                f"was called from \"{inspect.stack()[1][3]}\" function, "
                f"from module {func.__module__}")
            return result

        return wrapper

    @staticmethod
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

    @staticmethod
    def send_message(sock: socket, message: dict) -> None:
        """
        The function of encoding and sending a message,
        it takes a dictionary and sends it.

        :param sock: socket
        :param message:
        :return:
        """
        if not isinstance(message, dict):
            raise NonDictionaryInputError

        json_message = json.dumps(message)
        encoded_message = json_message.encode(ENCODING)
        sock.send(encoded_message)

    def _validate_port(self, listen_port: int) -> None:
        if not 1023 < listen_port < 65536:
            self.LOGGER.critical(
                f"Invalid port: {listen_port}. Allowed values: 1024 - 65535.")
            sys.exit(1)
