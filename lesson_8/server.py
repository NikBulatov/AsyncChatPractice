import logging
from socket import socket, AF_INET, SOCK_STREAM
from select import select
import logs.server_log_config
from services.common import get_message
from services.parsers import parse_server_arguments
from services.variables import SENDER, MAX_CONNECTIONS, RECEIVER
from services.server_helpers import process_client_message, process_message

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
    registered_accounts = {}

    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            LOGGER.info(f"Connection established with {client_address}")
            clients.append(client)

        recv_data, send_data, errors = [], [], []
        try:
            if clients:
                recv_data, send_data, errors = select(clients,
                                                      clients, [], 0)
        except OSError:
            print("\nA client close connection")

        if recv_data:
            for client_with_message in recv_data:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message,
                                           clients, registered_accounts)
                except Exception as e:
                    print(e)
                    LOGGER.info(
                        f"Client {client_with_message.getpeername()} "
                        f"closed connection.")
                    clients.remove(client_with_message)

        for message in messages:
            try:
                process_message(message, registered_accounts, send_data)
            except Exception as e:
                print(e)
                LOGGER.info(f"Connection with client {message[SENDER]}"
                            f" is lost")
                clients.remove(registered_accounts[message[RECEIVER]])
                del registered_accounts[message[RECEIVER]]
        messages.clear()


if __name__ == "__main__":
    main()
