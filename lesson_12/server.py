import logging
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from logs import server_log_config
from services import variables
from services.descriptors import Port
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
                        f"Connection with client {message[variables.RECEIVER]}"
                        f" is lost")
                    self.clients.remove(
                        self.names[message[variables.RECEIVER]])
                    del self.names[message[variables.RECEIVER]]
            self.messages.clear()

    def process_message(self, message: dict, listen_socks: list) -> None:
        if message[variables.RECEIVER] in self.names \
                and self.names[message[variables.RECEIVER]] in listen_socks:
            send_message(self.names[message[variables.RECEIVER]], message)
            LOGGER.info(
                f"Message's send to {message[variables.RECEIVER]} "
                f"by {message[variables.SENDER]}.")
        elif message[variables.RECEIVER] in self.names and \
                self.names[message[variables.RECEIVER]] not in listen_socks:
            raise ConnectionError
        else:
            LOGGER.error(
                f"User \"{message[variables.RECEIVER]}\" isn't registered,"
                f" message isn't send")

    def process_client_message(self, message: dict, client: socket):
        LOGGER.debug(f"Process client message: {message}")
        if variables.ACTION in message and variables.TIME in message:
            match message[variables.ACTION]:
                case variables.PRESENCE:
                    if variables.USER in message:
                        if message[variables.USER][variables.ACCOUNT_NAME] \
                                in self.names.keys():
                            response = variables.RESPONSE_400
                            response[
                                variables.ERROR] = "Current username is used"
                            send_message(client, response)
                            self.clients.remove(client)
                            client.close()
                        else:
                            self.names[message[variables.USER][
                                variables.ACCOUNT_NAME]] = client
                            send_message(client, variables.RESPONSE_200)
                case variables.MESSAGE:
                    if variables.RECEIVER in message \
                            and variables.SENDER in message \
                            and variables.MESSAGE_TEXT in message:
                        self.messages.append(message)
                case variables.EXIT:
                    if variables.ACCOUNT_NAME in message:
                        removed = self.names.pop(
                            message[variables.ACCOUNT_NAME], None)
                        self.clients.remove(removed)
                        removed.close()
                        del removed
                case variables.GET_CONTACTS:
                    if message[variables.USER][variables.ACCOUNT_NAME] \
                            in self.names.keys():
                        response = {variables.RESPONSE: variables.RESPONSE_202,
                                    variables.ALERT: self.names}
                        send_message(client, response)
                    else:
                        response = variables.RESPONSE_404
                        response[variables.ERROR] = "Not authorized"
                        send_message(client, response)
        else:
            response = variables.RESPONSE_400
            response[variables.ERROR] = "Invalid request"
            send_message(client, response)


def main():
    listen_address, listen_port = parse_server_arguments()
    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == "__main__":
    main()
