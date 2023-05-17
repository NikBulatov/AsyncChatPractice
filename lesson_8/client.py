import json
import logging
import sys
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

import logs.client_log_config
from helpers.parsers import parse_client_arguments
from helpers.services import (process_server_response,
                              get_message,
                              create_presence,
                              send_message, create_message,
                              message_from_server)
from helpers.errors import ServerError, RequiredFieldMissingError

LOGGER = logging.getLogger("client")


def main() -> None:
    server_address, server_port = parse_client_arguments()[2]
    listen_socket = (server_address, server_port)
    username = input("Input you username:\n")

    LOGGER.info(f"""Started client with parameters:
    - server address: {server_address},
    - server port: {server_port},
    - username: {username}""")
    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect(listen_socket)
        send_message(transport, create_presence())
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
    except ConnectionRefusedError:
        LOGGER.critical(
            f"Failed to connect to server {server_address}:{server_port}, "
            f"the destination source denied the connection request.")
        sys.exit(1)
    except (ValueError, json.JSONDecodeError):
        LOGGER.error("Can not decode server response")
        print("Can not decode server message")
    else:
        receiver = Thread(target=message_from_server,
                          args=(transport, username,))
        receiver.daemon = True
        receiver.start()

        sender = Thread(target=send_message, args=(transport, message_from_server(transport)))
        # match client_mode:
        #     case "send":
        #         print("Mode - send messages.")
        #     case "listen":
        #         print("Mode - received messages.")
        # while True:
        #     match client_mode:
        #         case "send":
        #             try:
        #                 send_message(transport, create_message(transport))
        #             except (ConnectionResetError,
        #                     ConnectionError,
        #                     ConnectionAbortedError):
        #                 LOGGER.error(
        #                     f"A connection with server "
        #                     f"with address: {server_address} was lost.")
        #                 sys.exit(1)
        #         case "listen":
        #             try:
        #                 message_from_server(get_message(transport))
        #             except (ConnectionResetError,
        #                     ConnectionError,
        #                     ConnectionAbortedError):
        #                 LOGGER.error(
        #                     f"A connection with server "
        #                     f"with address: {server_address} was lost.")
        #                 sys.exit(1)


if __name__ == "__main__":
    main()
