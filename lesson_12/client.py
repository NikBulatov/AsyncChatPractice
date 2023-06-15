import time
import json
import socket
import logging
from threading import Thread
from logs import client_log_config
from services.errors import *
from services.variables import *
from services.metaclasses import ClientVerifier
from services.parsers import parse_client_arguments
from services.common import send_message, get_message
from services.client_helpers import process_server_response, create_presence

LOGGER = logging.getLogger("client")


class ClientSender(Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def create_get_contacts_message(self):
        return {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def create_message(self):
        receiver = input("Input message receiver: ")
        message_text = input("Input message to send: ")
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            RECEIVER: receiver,
            TIME: time.time(),
            MESSAGE_TEXT: message_text
        }
        LOGGER.debug(f"Configure a message dict : {message_dict}")
        try:
            send_message(self.sock, message_dict)
            LOGGER.info(f"The message is send to {receiver}")
        except Exception as e:
            print(e)
            LOGGER.critical("Connection is lost")
            exit(1)

    def run(self):
        self.print_help()
        while True:
            command = input("Input a command: ")
            match command:
                case "message":
                    self.create_message()
                case 'help':
                    self.print_help()
                case "exit":
                    try:
                        send_message(self.sock, self.create_exit_message())
                    except Exception as e:
                        print(e, "LOL")
                        pass
                    print("Finished connection")
                    LOGGER.info("Finished running by user input")
                    time.sleep(.25)
                    break
                case "get_contacts":
                    try:
                        send_message(self.sock,
                                     self.create_get_contacts_message())
                    except Exception:
                        pass
                case _:
                    print(
                        "Invalid command. Try again "
                        "help - show supported commands.")

    def print_help(self):
        print("""Supported commands:
    message - send a message. Receiver and text will be asked later.
    help - show docs
    exit - quit the program
    get_contacts - get list of online clients""")


class ClientReader(Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE \
                        and SENDER in message and RECEIVER in message \
                        and MESSAGE_TEXT in message \
                        and message[RECEIVER] == self.account_name:
                    print(
                        f"\nGot a message by user {message[SENDER]}:"
                        f"\n{message[MESSAGE_TEXT]}")
                    LOGGER.info(
                        f"Got a message by user {message[SENDER]}:"
                        f"\n{message[MESSAGE_TEXT]}")
                else:
                    LOGGER.error(
                        f"Got invalid message by server: {message}")
            except IncorrectDataReceivedError:
                LOGGER.error(f"Failed to decode a message")
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                LOGGER.critical(f"Connection is lost")
                break


def main():
    print("CLI client is running.")

    server_address, server_port, client_name = parse_client_arguments()

    if not client_name:
        client_name = input("Input username: ")
    else:
        print(f"Client is running with username: {client_name}")

    LOGGER.info(
        f"Running client with params:"
        f" server address: {server_address},"
        f" port: {server_port},"
        f" username: {client_name}")

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_server_response(get_message(transport))
        LOGGER.info(
            f"Established connection with server. Response: {answer}")
        print(f"Established connection with server.")
    except json.JSONDecodeError:
        LOGGER.error('Failed decode JSON string')
        exit(1)
    except ServerError as error:
        LOGGER.error(
            f'While establishing connection server send error: {error.text}')
        exit(1)
    except RequiredFieldMissingError as missing_error:
        LOGGER.error(
            f"Missing field in server response {missing_error.missing_field}")
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(
            f"Failed established connection with server "
            f"{server_address}:{server_port}, remote host dropped connection")
        exit(1)
    else:
        module_receiver = ClientReader(client_name, transport)
        module_receiver.daemon = True
        module_receiver.start()

        module_sender = ClientSender(client_name, transport)
        module_sender.daemon = True
        module_sender.start()
        LOGGER.debug("Processes started")

        while True:
            time.sleep(.5)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == "__main__":
    main()
