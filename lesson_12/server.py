import datetime
import logging
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from logs import server_log_config
from services.descriptors import Port
from services.variables import *
from services.metaclasses import ServerVerifier
from services.parsers import parse_server_arguments
from services.common import get_message, send_message

LOGGER = logging.getLogger('server')


class Server(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_address, listen_port):
        self.addr = listen_address
        self.port = listen_port
        self.clients = []
        self.messages = []
        self.names = {}
        self.sock = None

    def init_socket(self):
        LOGGER.info(
            f"Server started, listening port: {self.port}, "
            f"listening address: {self.addr}. "
            f"If no address, listen all connections")

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((self.addr, self.port))
        self.sock.settimeout(0.5)
        self.sock.listen()

    def main_loop(self):
        self.init_socket()
        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f"Established connection with {client_address}")
                self.clients.append(client)

            recv_data, send_data, error = [], [], []
            try:
                if self.clients:
                    recv_data, send_data, errors = select(self.clients,
                                                          self.clients, [], 0)
            except OSError:
                pass

            if recv_data:
                for client_with_message in recv_data:
                    try:
                        self.process_client_message(
                            get_message(client_with_message),
                            client_with_message)
                    except Exception as e:
                        print(e)
                        LOGGER.info(
                            f"Client {client_with_message.getpeername()} "
                            f"close connection")
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.process_message(message, send_data)
                except Exception as e:
                    print(e)
                    LOGGER.info(
                        f"Connection with client {message[RECEIVER]} is lost")
                    self.clients.remove(self.names[message[RECEIVER]])
                    del self.names[message[RECEIVER]]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        if message[RECEIVER] in self.names \
                and self.names[message[RECEIVER]] in listen_socks:
            send_message(self.names[message[RECEIVER]], message)
            LOGGER.info(
                f"Message's send to {message[RECEIVER]} by {message[SENDER]}.")
        elif message[RECEIVER] in self.names and \
                self.names[message[RECEIVER]] not in listen_socks:
            raise ConnectionError
        else:
            LOGGER.error(f"User \"{message[RECEIVER]}\" isn't registered,"
                         f" message isn't send")

    def process_client_message(self, message, client):
        LOGGER.debug(f"Process client message: {message}")
        if ACTION in message and message[ACTION] == PRESENCE \
                and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = "Current username is used"
                send_message(client, response)
                self.clients.remove(client)
                client.close()
        elif ACTION in message and message[ACTION] == MESSAGE \
                and RECEIVER in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
        elif ACTION in message and message[ACTION] == EXIT \
                and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
        elif ACTION in message and message[ACTION] == GET_CONTACTS \
                and TIME in message:
            if message[USER][ACCOUNT_NAME] in self.names.keys():
                response = {RESPONSE: RESPONSE_202, ALERT: self.names}
                send_message(client, response)
            else:
                response = RESPONSE_404
                response[ERROR] = "Not authorized"
                send_message(client, response)
        else:
            response = RESPONSE_400
            response[ERROR] = "Invalid request"
            send_message(client, response)

    @staticmethod
    def request_handler(command: str) -> dict:
        request = {
            "action": None,
            "time": datetime.datetime.now(),
            "user_login": None
        }
        match command:
            case "get":
                request["action"] = "get_contacts"
            case "add":
                request["action"] = "add_contacts"
            case "del":
                request["action"] = "del_contacts"
            case _:
                raise ValueError("Unsupported command")
        return request

    def command_handler(self, ):
        pass


def main():
    listen_address, listen_port = parse_server_arguments()

    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == "__main__":
    main()
