import argparse
import json
import logging
import sys
import time
from socket import socket
from threading import Thread
import logs.client_log_config
from services.variables import *
from services.common import BaseSocket
from services.errors import *


class Client(BaseSocket):
    LOGGER = logging.getLogger("client")

    def __init__(self, listen_addr: str = "", listen_port: int = DEFAULT_PORT,
                 timeout: float = 0.5,
                 max_connections: int = MAX_CONNECTIONS):
        super().__init__(timeout, max_connections)
        self.__listen_addr, \
            self.__listen_port, \
            self._account_name = self.__parse_arguments(listen_port,
                                                        listen_addr)
        self.listen_socket = self.__listen_addr, self.__listen_port

    def __parse_arguments(self, port: int, addr: str) -> tuple:
        """
        Function to parse arguments from a command line.
        It returns tuple with passed ip address, port, mode

        :return: dict
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("addr", default=addr, nargs="?")
        parser.add_argument("port", default=port, type=int, nargs="?")
        parser.add_argument("-n", "--name", default=None, nargs="?")
        argspace = parser.parse_args(sys.argv[1:])
        server_address = argspace.addr
        server_port = argspace.port
        account_name = argspace.name

        self._validate_port(server_port)

        return server_address, server_port, account_name

    def _create_presence(self) -> dict:
        """
        Function to create a presence message

        :return: dict
        """

        self.LOGGER.debug(
            f"Message:{PRESENCE} is ready for user: {self._account_name}")
        return {ACTION: PRESENCE, TIME: time.time(),
                USER: {ACCOUNT_NAME: self._account_name}}

    def _create_exit(self) -> dict:
        """
        Function to create an exit message with the given account name
        :return:
        """
        return {ACTION: EXIT, TIME: time.time(),
                ACCOUNT_NAME: self._account_name}

    def _message_from_server(self) -> None:
        """
        Handler of messages from other users coming from the server
        :param client_account_name: dict
        :return:
        """
        while True:
            try:
                message = self.get_message(self.transport)
                if ACTION in message and message[ACTION] == MESSAGE and \
                        SENDER in message and RECEIVER in message \
                        and MESSAGE_TEXT in message \
                        and message[RECEIVER] == self._account_name:
                    print(f"Received message from user "
                          f"{message[SENDER]}:\n{message[MESSAGE_TEXT]}")
                    self.LOGGER.info(f"Received message from user "
                                     f"{message[SENDER]}:\n{message[MESSAGE_TEXT]}")
                else:
                    self.LOGGER.error(
                        f"Received incorrect message from server: {message}")
            except IncorrectDataReceivedError:
                self.LOGGER.error(f"Failed to decode received message")
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                self.LOGGER.critical("Connection is lost")
                break

    def _process_server_response(self, message: dict) -> str:
        """
        The function parses the server's response to the presence message,
        returns 200 if everything is OK, or raise an exception due to errors

        :param message: dict
        :return: str
        """
        self.LOGGER.debug(f"Parse server message: {message}")
        if isinstance(message, dict):
            if RESPONSE in message:
                if message[RESPONSE] == 200:
                    return "200 : OK"
                raise ServerError(f"400 : {message[ERROR]}")
        raise NonDictionaryInputError

    def _create_message(self, sock: socket, account_name: str):
        """
        The function requests the message text and returns it.
        It also closes script when user enter a similar command.
        :param sock: socket
        :param account_name: str
        """
        receiver = input("Input receiver name:\n\r")
        message = input("Input message. Input 'q' to stop command:\n\r")

        message_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            RECEIVER: receiver,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        self.LOGGER.debug(f'Message created: {message_dict}')
        try:
            self.send_message(sock, message_dict)
            self.LOGGER.info(f"Message was sent to {receiver}")
        except Exception as e:
            print(e)
            self.LOGGER.critical("Connection is lost")
            sys.exit(1)

    def user_interface(self):
        """
        Function to interact with user
        :return:
        """
        info_commands = """Supported commands:
            - "message" - send a message;
            - "help" - output help information about supported commands;
            - "exit" - quit the program
            """

        while True:
            command = input("Input command. To show help input \"help\":\n\r")
            match command:
                case "message":
                    self._create_message(self.transport, self._account_name)
                case "help":
                    print(info_commands)
                case "exit":
                    self.send_message(self.transport, self._create_exit())
                    print("Close connections")
                    self.LOGGER.info(
                        "Completion of work on the user's command.")
                    time.sleep(.5)
                    break
                case _:
                    print(
                        "Bad command. To show help information input \"help\"")

    def run(self):
        try:
            self._start(self.listen_socket)

            if not self._account_name:
                self._account_name = input(
                    "Input account name due to current name doesn't exist:\n\r")

            self.LOGGER.info(f"""Started client with parameters:
                        - server address: {self.__listen_addr},
                        - server port: {self.__listen_port},
                        - account name: {self._account_name}""")

            self.send_message(self.transport,
                              self._create_presence())
            self.LOGGER.debug(f"Send request to server: {self.__listen_addr}")

            answer = self._process_server_response(
                self.get_message(self.transport))
            self.LOGGER.info(
                f"A connection to the server has been established. "
                f"Server response: {answer}")
            print("A connection to the server has been established.")
        except json.JSONDecodeError:
            self.LOGGER.error("Failed to decode the received JSON string.")
            sys.exit(1)
        except ServerError as error:
            self.LOGGER.error(f"The server returned an error"
                              f" while establishing a connection: {error.text}")
            sys.exit(1)
        except RequiredFieldMissingError as missing_error:
            self.LOGGER.error(
                f"A required field is missing in the server response: "
                f"{missing_error.missing_field}")
            sys.exit(1)
        except (ConnectionRefusedError, ConnectionError):
            self.LOGGER.critical(
                f"Failed to connect to server {self.__listen_addr}:{self.__listen_port}, "
                f"the destination source denied the connection request.")
            sys.exit(1)
        else:
            receiver = Thread(target=self._message_from_server)
            receiver.daemon = True
            receiver.start()

            sender = Thread(target=self.cmd_interface,
                            args=(self.transport, self._account_name))
            sender.daemon = True
            sender.start()
            self.LOGGER.debug("Threads started")

            while True:
                time.sleep(.5)
                if receiver.is_alive() and sender.is_alive():
                    continue
                break


def main():
    client = Client()
    client.run()


if __name__ == "__main__":
    main()
