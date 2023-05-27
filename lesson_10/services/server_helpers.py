import logging
from socket import socket

from .common import log, send_message
from .variables import (ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, EXIT,
                        SENDER, MESSAGE_TEXT, RECEIVER, ERROR, MESSAGE,
                        RESPONSE_200, RESPONSE_400)

LOGGER = logging.getLogger("server")


@log
def process_client_message(message: dict, messages: list,
                           client: socket, clients: list,
                           names: dict) -> None:
    """
    Handler of messages from clients, receives message from the client,
    validate it, sends a dictionary response to the client.

    :param message:
    :param messages:
    :param clients:
    :param names:
    :param client:
    """
    LOGGER.debug(f"Parse client message {message}")

    # process presence request
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:

        # check account name
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = "Current account name is used"
            send_message(client, response)
            clients.remove(client)
            client.close()

    # process message request
    elif ACTION in message and message[ACTION] == MESSAGE \
            and RECEIVER in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages.append(message)

    # process exit request
    elif ACTION in message and message[ACTION] == EXIT \
            and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]

    # process bad request
    else:
        response = RESPONSE_400
        response[ERROR] = "Bad request"
        send_message(client, response)


@log
def process_message(message: dict, registered_accounts: dict,
                    listen_sockets: list[socket]) -> None:
    """
    Function to send message tp the client
    :param message:
    :param registered_accounts:
    :param listen_sockets:
    :return:
    """
    if message[RECEIVER] in registered_accounts \
            and registered_accounts[message[RECEIVER]] in listen_sockets:
        send_message(registered_accounts[message[RECEIVER]], message)
        LOGGER.info(f"Message was sent \"{message[RECEIVER]}\" "
                    f"by user \"{message[SENDER]}\"")
    elif message[RECEIVER] in registered_accounts \
            and registered_accounts[message[RECEIVER]] not in listen_sockets:
        raise ConnectionError
    else:
        LOGGER.error(f"User {message[RECEIVER]} is not registered on server, "
                     f"message isn't sent")
