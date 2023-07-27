import sys
import time
import logging
import argparse
from socket import socket

sys.path.append("../")

from services.common import log, send_request
from services.variables import *
from services.errors import ServerError, NonDictionaryInputError

LOGGER = logging.getLogger("client")


@log
def parse_client_args() -> tuple:
    """
    Return tuple with passed arguments via CML
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", default="localhost", type=str, nargs="?")
    parser.add_argument("port", default=DEFAULT_PORT, type=int, nargs="?")
    parser.add_argument("-n", "--name", default=None, type=str, nargs="?")
    parser.add_argument("-p", "--password", default="", type=str, nargs="?")
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_password = namespace.password

    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f"Try to run client with incorrect port value: {server_port}. "
            f"Allowed values are from 1024 to 65535. Client closing."
        )
        exit(1)

    return server_address, server_port, client_name, client_password


@log
def create_presence(account_name: str) -> dict:
    """
    Create a presence message with the given account name

    :param account_name:
    :return: dict
    """

    LOGGER.debug(f"Message:{PRESENCE} is ready for user: {account_name}")
    return {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {ACCOUNT_NAME: account_name}
    }


@log
def create_exit(account_name: str) -> dict:
    """
    Create an exit message with the given account name
    :param account_name:
    :return: dict
    """
    return {ACTION: EXIT, TIME: time.time(), ACCOUNT_NAME: account_name}


@log
def process_server_response(message: dict) -> str:
    """
    Parse the server's response to the presence message,
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
def create_message(sock: socket, account_name: str):
    """
    Request the message text and returns it.
    It also closes script when user enter a similar command.

    :param sock: socket
    :param account_name: str
    """
    receiver = input("Input receiver name:\n\r")
    message = input("Input message. Input 'q' to stop command:\n\r")

    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        RECEIVER: receiver,
        TIME: time.time(),
        MESSAGE_TEXT: message,
    }
    LOGGER.debug(f"Message created: {message_dict}")
    try:
        send_request(sock, message_dict)
        LOGGER.info(f"Message was sent to {receiver}")
    except Exception as e:
        print(e)
        LOGGER.critical("Connection is lost")
        sys.exit(1)
