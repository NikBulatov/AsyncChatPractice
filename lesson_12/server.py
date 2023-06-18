import logging
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from logs import server_log_config
from services import variables
from services.descriptors import Port
from services.metaclasses import ServerVerifier
from services.parsers import parse_server_arguments
from services.common import get_response, send_message

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
                        self.request_handler(
                            get_response(client_with_message),
                            client_with_message)
                    except Exception:
                        LOGGER.info(
                            f"Client {client_with_message.getpeername()} "
                            f"close connection")
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.process_message(message, send_data)
                except Exception:
                    LOGGER.info(
                        f"Connection with client {message[variables.RECEIVER]}"
                        f" is lost")
                    self.clients.remove(
                        self.names[message[variables.RECEIVER]])
                    del self.names[message[variables.RECEIVER]]
            self.messages.clear()

    def process_message(self, message: dict, listen_socks: list) -> None:
        if message[variables.RECEIVER] in self.names:
            if self.names[message[variables.RECEIVER]] in listen_socks:
                send_message(self.names[message[variables.RECEIVER]], message)
                LOGGER.info(
                    f"Message's send to {message[variables.RECEIVER]} "
                    f"by {message[variables.SENDER]}.")
            elif self.names[message[variables.RECEIVER]] not in listen_socks:
                raise ConnectionError
        else:
            LOGGER.error(
                f"User \"{message[variables.RECEIVER]}\" isn't registered,"
                f" message isn't send")

    def request_handler(self, request: dict, client: socket):
        LOGGER.debug(f"Process client message: {request}")
        if variables.ACTION in request and variables.TIME in request:
            match request[variables.ACTION]:
                case variables.PRESENCE:
                    if variables.USER in request:
                        if (request[variables.USER][variables.ACCOUNT_NAME]
                                in self.names.keys()):
                            response = variables.RESPONSE_400
                            response[
                                variables.ERROR] = "Current username is used"
                            send_message(client, response)
                            self.clients.remove(client)
                            client.close()
                        else:
                            self.names[request[variables.USER][
                                variables.ACCOUNT_NAME]] = client
                            send_message(client, variables.RESPONSE_200)
                case variables.MESSAGE:
                    if (variables.RECEIVER in request
                            and variables.SENDER in request
                            and variables.MESSAGE_TEXT in request):
                        self.messages.append(request)
                case variables.EXIT:
                    if variables.ACCOUNT_NAME in request:
                        removed = self.names.pop(
                            request[variables.ACCOUNT_NAME], None)
                        self.clients.remove(removed)
                        removed.close()
                        del removed
                case variables.GET_CONTACTS:
                    if request[variables.USER_LOGIN] in self.names.keys():
                        response = {variables.RESPONSE: 202,
                                    variables.ALERT: list(self.names.keys())}
                        send_message(client, response)
                    else:
                        response = variables.RESPONSE_404
                        response[variables.ERROR] = "Not authorized"
                        send_message(client, response)
                case variables.ADD_CONTACT:
                    if request[variables.USER_LOGIN] in self.names.keys():
                        if not request[variables.USER_ID] in self.names.keys():
                            self.names[request[variables.USER_ID]] = None
                            response = {variables.RESPONSE: 201}
                            send_message(client, response)
                        else:
                            response = variables.RESPONSE_400
                            response[
                                variables.ERROR] = "Current user_id is used"
                case variables.DEL_CONTACT:
                    if request[variables.USER_LOGIN] in self.names.keys():
                        try:
                            removed = self.names.pop(
                                request[variables.ACCOUNT_NAME], None)
                            self.clients.remove(removed)
                            removed.close()
                        except (AttributeError, ValueError):
                            response = variables.RESPONSE_400
                            response[
                                variables.ERROR] = "Current user_id doesn't exist"
                        else:
                            response = variables.RESPONSE_200
                        finally:
                            del removed
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
