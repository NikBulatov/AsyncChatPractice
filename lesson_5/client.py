import sys
import json
import socket
import time
import logs.client_log_config
import logging
from extensions import (ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME,
                        RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT,
                        get_message, send_message)

LOGGER = logging.getLogger("client")


def create_presence(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(f'Message:{PRESENCE} is ready for user: {account_name}')
    return out


def process_answer(message):
    LOGGER.debug(f"Parse server message: {message}")
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def parse_arguments():
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            LOGGER.critical(
                f'Invalid port number: {server_port}. Client closed!')
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print('Invalid port number')
        sys.exit(1)

    return {"ip_addr": server_address, "port": server_port}


def main():
    ip_addr, port = parse_arguments().values()
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((ip_addr, port))
    message_to_server = create_presence()
    send_message(transport, message_to_server)
    LOGGER.debug(f"Send request to server: {ip_addr}")
    try:
        answer = process_answer(get_message(transport))
        LOGGER.info("Got server response")
        print(answer)
    except (ValueError, json.JSONDecodeError):
        LOGGER.error("Can not decode server response")
        print('Can not decode server message')


if __name__ == '__main__':
    LOGGER.info("FYI")
    main()
