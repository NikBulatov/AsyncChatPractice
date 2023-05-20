import argparse
import logging
import sys
from socket import socket, AF_INET, SOCK_STREAM
from select import select
import logs.server_log_config
from services.common import get_message, BaseObject
from services.variables import *


class Server(BaseObject):
    CLIENTS = []
    LOGGER = logging.getLogger("server")
    MESSAGES = []
    REGISTERED_ACCOUNTS = {}

    def __init__(self,
                 listen_addr: str = "",
                 listen_port: int = DEFAULT_PORT,
                 timeout: float = 0.5,
                 max_connections: int = MAX_CONNECTIONS):
        self.transport = socket(AF_INET, SOCK_STREAM)
        self.listen_socket = self.__parse_server_arguments(listen_port,
                                                           listen_addr)
        self.timeout = timeout
        self.max_connections = max_connections

    def _start(self):
        self.transport.bind(self.listen_socket)
        self.transport.settimeout(0.5)
        self.transport.listen(MAX_CONNECTIONS)
        return self.transport

    def run(self):
        self.transport = self._start()
        self.LOGGER.info(
            f"""Running server,
                    - port for connection: {self.listen_socket[1]};"
                    - await connections by address: {self.listen_socket[0]}.
                If no address, await connections by anyone""")
        while True:
            try:
                client, client_address = self.transport.accept()
            except OSError:
                pass
            else:
                self.LOGGER.info(
                    f"Connection established with {client_address}")
                self.CLIENTS.append(client)

            recv_data, send_data, errors = [], [], []
            try:
                if self.CLIENTS:
                    recv_data, send_data, errors = select(self.CLIENTS,
                                                          self.CLIENTS, [], 0)
            except OSError:
                print("\nA client close connection")

            if recv_data:
                for client_with_message in recv_data:
                    try:
                        self._process_client_message(
                            get_message(client_with_message),
                            self.MESSAGES, client_with_message,
                            self.CLIENTS, self.REGISTERED_ACCOUNTS)
                    except Exception as e:
                        print(e)
                        self.LOGGER.info(
                            f"Client {client_with_message.getpeername()} "
                            f"closed connection.")
                        self.CLIENTS.remove(client_with_message)

            for message in self.MESSAGES:
                try:
                    self._process_message(message, self.REGISTERED_ACCOUNTS,
                                          send_data)
                except Exception as e:
                    print(e)
                    self.LOGGER.info(
                        f"Connection with client {message[SENDER]}"
                        f" is lost")
                    self.CLIENTS.remove(
                        self.REGISTERED_ACCOUNTS[message[RECEIVER]])
                    del self.REGISTERED_ACCOUNTS[message[RECEIVER]]
            self.MESSAGES.clear()

    def _process_client_message(self, message: dict, messages: list,
                                client: socket, clients: list,
                                names: dict) -> None:
        """
            Handler of messages from clients, receives message from the client,
            validate it, sends a dictionary response to the client.

            :param message:
            :param messages:
            :param clients:
            :param names:
            :param client:
            """
        self.LOGGER.debug(f"Parse client message {message}")

        # process presence request
        if ACTION in message and message[
            ACTION] == PRESENCE and TIME in message \
                and USER in message:

            # check account name
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                self.send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = "Current account name is used"
                self.send_message(client, response)
                clients.remove(client)
                client.close()

        # process message request
        elif ACTION in message and message[ACTION] == MESSAGE \
                and RECEIVER in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            messages.append(message)

        # process exit request
        elif ACTION in message and message[ACTION] == EXIT \
                and ACCOUNT_NAME in message:
            clients.remove(names[message[ACCOUNT_NAME]])
            names[message[ACCOUNT_NAME]].close()
            del names[message[ACCOUNT_NAME]]

        # process bad request
        else:
            response = RESPONSE_400
            response[ERROR] = "Bad request"
            self.send_message(client, response)

    def _process_message(self, message: dict, registered_accounts: dict,
                         listen_sockets: list[socket]) -> None:
        """
        Function to send message to the client
        :param message:
        :param registered_accounts:
        :param listen_sockets:
        :return:
        """
        if message[RECEIVER] in registered_accounts \
                and registered_accounts[message[RECEIVER]] in listen_sockets:
            self.send_message(registered_accounts[message[RECEIVER]], message)
            self.LOGGER.info(f"Message was sent \"{message[RECEIVER]}\" "
                             f"by user \"{message[SENDER]}\"")
        elif message[RECEIVER] in registered_accounts \
                and registered_accounts[message[RECEIVER]] \
                not in listen_sockets:
            raise ConnectionError
        else:
            self.LOGGER.error(
                f"User {message[RECEIVER]} is not registered on server, "
                f"message isn't sent")

    def __parse_server_arguments(self, port, addr) -> tuple:
        """
        Function to parse arguments from a command line.
        It returns tuple with passed ip address and port

        :return: dict
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-p", default=port, type=int, nargs="?")
        parser.add_argument("-a", default=addr, nargs="?")
        argspace = parser.parse_args(sys.argv[1:])
        listen_address = argspace.a
        listen_port = argspace.p

        self._validate_port(listen_port)

        return listen_address, listen_port


def main() -> None:
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
