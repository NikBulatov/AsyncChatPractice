import binascii
import hashlib
import hmac
import sys
import time
import socket
import logging
from json import JSONDecodeError
from threading import Thread, Lock
from Crypto.PublicKey.RSA import RsaKey
from PyQt6.QtCore import QObject, pyqtSignal

sys.path.append("../")
from logs import client_log_config
from services.errors import *
from services.variables import *
from services.common import send_request, get_response
from client.client_models import ClientDatabase

LOGGER = logging.getLogger("client")
socket_lock = Lock()


class Client(Thread, QObject):
    new_message = pyqtSignal(dict)
    message_205 = pyqtSignal()
    connection_lost = pyqtSignal()

    def __init__(self,
                 port: int,
                 ip_address: str,
                 database: ClientDatabase,
                 username: str,
                 password: str,
                 keys: RsaKey):
        Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        self.password = password
        self.keys = keys
        self.transport = None
        self.connection_init(ip_address, port)

        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                LOGGER.critical("Connection with server is lost")
                raise ServerError("Connection with server is lost")
            LOGGER.error("Timeout updating users list")
        except JSONDecodeError:
            LOGGER.critical("Connection with server is lost")
            raise ServerError("Connection with server is lost")
        self.running = True

    def connection_init(self, ip: str, port: int) -> None:
        """
        Wait and init any connection with clients on passed ip address and port
        :param ip: listening ip address
        :param port: listening port
        :return:
        """
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.settimeout(5)

        connected = False
        for i in range(5):
            LOGGER.info(f"Connection trying №{i + 1}")
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(0.25)

        if not connected:
            LOGGER.critical("Failed to establish a connection with the server")
            raise ServerError(
                "Failed to establish a connection with the server")

        LOGGER.debug("A connection has established with server")
        LOGGER.debug("Starting auth dialog")

        passwd_bytes = self.password.encode("utf-8")
        salt = self.username.lower().encode("utf-8")
        passwd_hash = hashlib.pbkdf2_hmac("sha512", passwd_bytes, salt, 10000)
        passwd_hash_string = binascii.hexlify(passwd_hash)

        pubkey = self.keys.publickey().export_key().decode("ascii")

        with socket_lock:
            request = {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: self.username,
                    PUBLIC_KEY: pubkey
                }
            }
            try:
                send_request(self.transport, request)
                response = get_response(self.transport)
                if RESPONSE in response:
                    match response[RESPONSE]:
                        case 400:
                            raise ServerError(response[ERROR])
                        case 511:
                            response_data = response[DATA]
                            hash = hmac.new(
                                passwd_hash_string,
                                response_data.encode("utf-8"),
                                "MD5"
                            )
                            digest = hash.digest()
                            my_response = RESPONSE_511
                            my_response[DATA] = binascii.b2a_base64(
                                digest).decode("ascii")
                            send_request(self.transport, my_response)
                            self.process_server_response(
                                get_response(self.transport)
                            )
            except (OSError, JSONDecodeError) as e:
                LOGGER.debug(f"Connection error.", exc_info=e)
                raise ServerError("Failed to authenticate")

    def process_server_response(self, message: dict) -> None:
        """
        Generate response by server on received message
        or process message request
        Possible responses:\n
        200 - OK\n
        400 - Bad request\n
        205 - Reset Content
        :param message: dict message
        :return:
        """
        LOGGER.debug(f"Parse server message: {message}")
        if isinstance(message, dict):
            if RESPONSE in message:
                match message[RESPONSE]:
                    case 200:
                        return
                    case 400:
                        raise ServerError(f"{message[ERROR]}")
                    case 205:
                        self.user_list_update()
                        self.contacts_list_update()
                        self.message_205.emit()
                    case _:
                        LOGGER.debug(
                            f"Received unknown code "
                            f"{message[RESPONSE]}"
                        )

            elif (
                    ACTION in message
                    and message[ACTION] == MESSAGE
                    and SENDER in message
                    and RECEIVER in message
                    and MESSAGE_TEXT in message
                    and message[RECEIVER] == self.username
            ):
                LOGGER.debug(
                    f"Received a message by user "
                    f"{message[SENDER]}:"
                    f"{message[MESSAGE_TEXT]}"
                )
                self.new_message.emit(message)

    def contacts_list_update(self) -> None:
        """
        Contact list update request handler
        :return:
        """
        LOGGER.debug(f"Contact list request for user {self.name}")
        request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        LOGGER.debug(f"Request is {request}")
        with socket_lock:
            send_request(self.transport, request)
            response = get_response(self.transport)
        LOGGER.debug(f"Response is received {response}")
        if (
                RESPONSE in response
                and response[RESPONSE] == 202
        ):
            for contact in response[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            LOGGER.error("Failed to update contact list")

    def user_list_update(self) -> None:
        """
        Known contact list update request handler
        :return:
        """
        LOGGER.debug(f"Known contact list reqeust {self.username}")
        request = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_request(self.transport, request)
            response = get_response(self.transport)
        if (
                RESPONSE in response
                and response[RESPONSE] == 202
        ):
            self.database.add_users(response[LIST_INFO])
        else:
            LOGGER.error("Failed to update known contact list")

    def key_request(self, user: str) -> str | bytes | None:
        """
        Key request request handler
        :param user: a username
        :return:
        """
        LOGGER.debug(f"Request public key for {user}")
        request = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with socket_lock:
            send_request(self.transport, request)
            response = get_response(self.transport)
        if (
                RESPONSE in response
                and response[RESPONSE] == 511
        ):
            return response[DATA]
        else:
            LOGGER.error(f"Failed to get recipient pubkey by {user}.")

    def add_contact(self, contact: str) -> None:
        """
        Add contact request handler
        :param contact:
        :return:
        """
        request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        LOGGER.debug(f"Creating a contact {request[ACCOUNT_NAME]}")
        with socket_lock:
            send_request(self.transport, request)
            self.process_server_response(get_response(self.transport))

    def remove_contact(self, contact: str) -> None:
        """
        Remove contact request handler
        :param contact: a contact name
        :return:
        """
        request = {
            ACTION: DEL_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        LOGGER.debug(f"Removing a contact {request[ACCOUNT_NAME]}")
        with socket_lock:
            send_request(self.transport, request)
            self.process_server_response(get_response(self.transport))

    def transport_shutdown(self) -> None:
        """
        Exit request handler
        :return:
        """
        self.running = False
        request = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_request(self.transport, request)
            except OSError:
                LOGGER.error("Failed to send message")
        LOGGER.debug("Client close connection")
        time.sleep(0.5)

    def send_message(self, receiver: str, message_text: str) -> None:
        """
        Message request handler
        :param receiver: a receiver name
        :param message_text:
        :return:
        """
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            RECEIVER: receiver,
            TIME: time.time(),
            MESSAGE_TEXT: message_text
        }
        LOGGER.debug(f"Configure a message dict: {message_dict}")

        with socket_lock:
            send_request(self.transport, message_dict)
            self.process_server_response(get_response(self.transport))
            LOGGER.info(
                f"Message has been sent to {message_dict[RECEIVER]}"
            )

    def run(self) -> None:
        LOGGER.debug("Start process - message received by server.")
        while self.running:
            time.sleep(0.75)
            message = None

            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_response(self.transport)
                except OSError as e:
                    if e.errno:
                        LOGGER.critical("Connection is lost")
                        self.running = False
                        self.connection_lost.emit()
                except (
                        ConnectionError,
                        ConnectionAbortedError,
                        ConnectionResetError,
                        JSONDecodeError,
                        TypeError,
                ):
                    LOGGER.debug("Connection is lost")
                    self.running = False
                    self.connection_lost.emit()
                finally:
                    self.transport.settimeout(5)

            if message:
                LOGGER.debug(f"Received message by server: {message}")
                self.process_server_response(message)
