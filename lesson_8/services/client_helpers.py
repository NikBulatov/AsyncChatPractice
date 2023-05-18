import json
import logging
import sys
import time
from socket import socket

from .common import log, send_message, get_message
from .variables import (ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, EXIT,
                        SENDER, MESSAGE_TEXT, RECEIVER, ERROR, MESSAGE,
                        RESPONSE)
from .errors import (ServerError, NonDictionaryInputError,
                     IncorrectDataReceivedError)

LOGGER = logging.getLogger("client")


@log
def create_presence(account_name: str) -> dict:
    """
    Function to create a presence message with the given account name

    :param account_name: str
    :return: dict
    """

    LOGGER.debug(f"Message:{PRESENCE} is ready for user: {account_name}")
    return {ACTION: PRESENCE, TIME: time.time(),
            USER: {ACCOUNT_NAME: account_name}}


@log
def create_exit(account_name: str) -> dict:
    """
    Function to create an exit message with the given account name
    :param account_name:
    :return:
    """
    return {ACTION: EXIT, TIME: time.time(), ACCOUNT_NAME: account_name}


@log
def message_from_server(sock: socket, client_account_name: str) -> None:
    """
    Handler of messages from other users coming from the server
    :param sock
    :param client_account_name: dict
    :return:
    """
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and RECEIVER in message \
                    and MESSAGE_TEXT in message \
                    and message[RECEIVER] == client_account_name:
                print(f"Received message from user "
                      f"{message[SENDER]}:\n{message[MESSAGE_TEXT]}")
                LOGGER.info(f"Received message from user "
                            f"{message[SENDER]}:\n{message[MESSAGE_TEXT]}")
            else:
                LOGGER.error(
                    f"Received incorrect message from server: {message}")
        except IncorrectDataReceivedError:
            LOGGER.error(f"Failed to decode received message")
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            LOGGER.critical("Connection is lost")
            break


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
def create_message(sock: socket, account_name: str):
    """
    The function requests the message text and returns it.
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
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Message created: {message_dict}')
    try:
        send_message(sock, message_dict)
        LOGGER.info(f"Message was sent to {receiver}")
    except Exception as e:
        print(e)
        LOGGER.critical("Connection is lost")
        sys.exit(1)


@log
def cmd_interface(sock: socket, account_name: str) -> None:
    """
    Function to interact with user
    :param sock:
    :param account_name:
    :return:
    """
    info_commands = """Supported commands:
    - "message" - send a message;
    - "help" - output help information about supported commands;
    - "exit" - quit the program
    """

    while True:
        command = input("Input command. To show help input \"help\":\n\r")
        match command:
            case "message":
                create_message(sock, account_name)
            case "help":
                print(info_commands)
            case "exit":
                send_message(sock, create_exit(account_name))
                print("Close connections")
                LOGGER.info("Completion of work on the user's command.")
                time.sleep(.5)
                break
            case _:
                print("Bad command. To show help information input \"help\"")
