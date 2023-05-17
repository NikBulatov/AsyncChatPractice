import json
import logging
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

import logs.client_log_config
from services.parsers import parse_client_arguments
from services.client_helpers import (process_server_response, create_presence,
                                     send_message, message_from_server,
                                     cmd_interface)
from services.common import get_message
from services.errors import ServerError, RequiredFieldMissingError

LOGGER = logging.getLogger("client")


def main() -> None:
    server_address, server_port, account_name = parse_client_arguments()
    listen_socket = (server_address, server_port)

    if not account_name:
        account_name = input(
            "Input account name due to current name doesn't exist:\n\r")

    LOGGER.info(f"""Started client with parameters:
    - server address: {server_address},
    - server port: {server_port},
    - account name: {account_name}""")
    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect(listen_socket)

        send_message(transport, create_presence(account_name))
        LOGGER.debug(f"Send request to server: {listen_socket[0]}")

        answer = process_server_response(get_message(transport))
        LOGGER.info(f"A connection to the server has been established. "
                    f"Server response: {answer}")
        print("A connection to the server has been established.")
    except json.JSONDecodeError:
        LOGGER.error("Failed to decode the received JSON string.")
        sys.exit(1)
    except ServerError as error:
        LOGGER.error(f"The server returned an error"
                     f" while establishing a connection: {error.text}")
        sys.exit(1)
    except RequiredFieldMissingError as missing_error:
        LOGGER.error(
            f"A required field is missing in the server response: "
            f"{missing_error.missing_field}")
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(
            f"Failed to connect to server {server_address}:{server_port}, "
            f"the destination source denied the connection request.")
        sys.exit(1)
    else:
        receiver = Thread(target=message_from_server, args=(transport,
                                                            account_name))
        receiver.daemon = True
        receiver.start()

        sender = Thread(target=cmd_interface, args=(transport, account_name))
        sender.daemon = True
        sender.start()
        LOGGER.debug("Threads started")

        while True:
            time.sleep(1.05)
            if receiver.is_alive() and sender.is_alive():
                continue
            break


if __name__ == "__main__":
    main()
