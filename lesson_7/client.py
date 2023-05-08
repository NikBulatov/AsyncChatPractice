import json
import logging
import time
from socket import socket, AF_INET, SOCK_STREAM

from services import (get_message, process_answer,
                      parse_client_arguments, create_presence, send_message)
import logs.client_log_config

LOGGER = logging.getLogger("client")


def main() -> None:
    listen_socket = parse_client_arguments()
    for _ in range(10):
        time.sleep(0.5)
        with socket(AF_INET, SOCK_STREAM) as transport:
            transport.connect(listen_socket)
            request_data = create_presence()
            send_message(transport, request_data)
            LOGGER.debug(f"Send request to server: {listen_socket[0]}")
            try:
                answer = process_answer(get_message(transport))
                LOGGER.info("Got server response")
                print('Response:', answer)
            except (ValueError, json.JSONDecodeError):
                LOGGER.error("Can not decode server response")
                print("Can not decode server message")


if __name__ == "__main__":
    main()
