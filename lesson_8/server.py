import logging
from socket import socket, AF_INET, SOCK_STREAM
import time
import select
import logs.server_log_config
from helpers.parsers import parse_server_arguments
from helpers.variables import (MESSAGE_TEXT, TIME, SENDER, ACTION, MESSAGE,
                               MAX_CONNECTIONS)
from helpers.services import process_client_message, get_message, send_message

LOGGER = logging.getLogger("server")


def main() -> None:
    listen_socket = parse_server_arguments()

    transport = socket(AF_INET, SOCK_STREAM)
    LOGGER.info(f"""Running server,
    - port for connection: {listen_socket[1]};"
    - await connections by address: {listen_socket[0]}.
If no address, await connections by anyone""")
    transport.bind(listen_socket)
    transport.settimeout(0.5)

    clients = []
    messages = []

    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            print("Timeout expired")
        else:
            LOGGER.info(f"Connection established with {client_address}")
            clients.append(client)

        recv_data, send_data, errors = [], [], []
        try:
            if clients:
                recv_data, send_data, errors = select.select(clients,
                                                             clients, [], 0)
        except OSError:
            print("\nA client close connection")

        if recv_data:
            for client_with_message in recv_data:
                try:
                    process_client_message(
                        get_message(client_with_message),
                        messages, client_with_message)
                except Exception as e:
                    print(e)
                    LOGGER.info(
                        f"Client {client_with_message.getpeername()} "
                        f"closed connection.")
                    clients.remove(client_with_message)

        if messages and send_data:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data:
                try:
                    send_message(waiting_client, message)
                except Exception as e:
                    print(e)
                    LOGGER.info(f"Client {waiting_client.getpeername()} "
                                f"closed connection.")
                    clients.remove(waiting_client)


if __name__ == "__main__":
    main()
