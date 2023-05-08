import json
import logging
import select

from variables import RESPONSE, ERROR
from services import (read_requests, write_responses, parse_server_arguments,
                      init_listen_socket, process_client_message,
                      get_message, send_message)
import logs.server_log_config

LOGGER = logging.getLogger("server")


def main() -> None:
    CLIENTS = []
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
            try:
                message_from_client = get_message(client)
                LOGGER.debug(f"Got message: {message_from_client}")
                print(message_from_client)

                response = process_client_message(message_from_client)
                LOGGER.debug(f"Send response: {response}")

                send_message(client, response)
                LOGGER.debug(f"Connection with {client_address} is closing")
            except (ValueError, json.JSONDecodeError):
                LOGGER.error(f"Got invalid data by {client_address}")
                response = {
                    RESPONSE: 400,
                    ERROR: "Bad Request"
                }
                send_message(client, response)
        finally:
            r, w, e = [], [], []
            try:
                r, w, e = select.select([], CLIENTS, [], 10)
            except OSError:
                print("\nA client close connection")
            requests = read_requests(r, CLIENTS)
            if requests:
                write_responses(requests, w, CLIENTS)


if __name__ == "__main__":
    main()
