import socket
import sys
import json
from extensions import (ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS,
                        PRESENCE, TIME, USER, ERROR, DEFAULT_PORT,
                        get_message, send_message)


def process_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def parse_arguments():
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('Port needed')
        sys.exit(1)
    except ValueError:
        print('Invalid port value')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = int(sys.argv[sys.argv.index('-a') + 1])
        else:
            listen_address = ''

    except IndexError:
        print('IP address needed')
        sys.exit(1)

    return {"ip_addr": listen_address, "port": listen_port}


def main():
    listen_address, listen_port = parse_arguments().values()

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            print(message_from_client)
            response = process_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Incorrect message received')
            client.close()


if __name__ == '__main__':
    main()
