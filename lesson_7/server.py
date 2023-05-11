import json
import logging
import time

import select

from variables import MESSAGE_TEXT, TIME, SENDER, ACTION, MESSAGE
from services import (parse_server_arguments,
                      init_listen_socket, process_client_message,
                      get_message, send_message)
import logs.server_log_config

LOGGER = logging.getLogger("server")


def main() -> None:
    CLIENTS = []
    MESSAGES = []

    listen_socket = parse_server_arguments()

    transport = init_listen_socket(listen_socket)
    LOGGER.info(f"Running server, port for connection: {listen_socket[1]}, "
                f"await connections by address: {listen_socket[0]}. "
                f"If no address, await connections by anyone")

    while True:
        try:
            client, client_address = transport.accept()
            LOGGER.info(f"Connection established with {client_address}")
        except OSError:
            print("Timeout expired")
        else:
            print(f"Received request by {client_address}")
            CLIENTS.append(client)

            recv_data, send_data, errors = [], [], []
            try:
                recv_data, send_data, errors = select.select(CLIENTS, CLIENTS,
                                                             [],
                                                             10)
            except OSError:
                print("\nA client close connection")

            if recv_data:
                for client_with_message in recv_data:
                    try:
                        process_client_message(get_message(client_with_message),
                                               MESSAGES, client_with_message)
                    except Exception as e:
                        print(e)
                        LOGGER.info(
                            f'Client {client_with_message.getpeername()} '
                            f'closed connection.')
                        CLIENTS.remove(client_with_message)

            if MESSAGES and send_data:
                message = {
                    ACTION: MESSAGE,
                    SENDER: MESSAGES[0][0],
                    TIME: time.time(),
                    MESSAGE_TEXT: MESSAGES[0][1]
                }
                del MESSAGES[0]
                for waiting_client in send_data:
                    try:
                        send_message(waiting_client, message)
                    except Exception as e:
                        print(e)
                        LOGGER.info(
                            f'Client {waiting_client.getpeername()} closed connection.')
                        CLIENTS.remove(waiting_client)


if __name__ == "__main__":
    main()
