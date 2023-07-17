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
from services import variables
from services.common import send_message, get_response
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

    def connection_init(self, ip: str, port: int):
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

        LOGGER.debug(f"Passwd hash ready: {passwd_hash_string}")

        pubkey = self.keys.publickey().export_key().decode("ascii")

        with socket_lock:
            request = self.create_request(variables.PRESENCE)
            request[variables.USER].update({variables.PUBLIC_KEY: pubkey})
            LOGGER.debug(f"Presence message = {request}")
            try:
                send_message(self.transport, request)
                response = get_response(self.transport)
                LOGGER.debug(f"Server response = {response}.")
                if variables.RESPONSE in response:
                    if response[variables.RESPONSE] == 400:
                        raise ServerError(response[variables.ERROR])
                    elif response[variables.RESPONSE] == 511:
                        response_data = response[variables.DATA]
                        hash = hmac.new(
                            passwd_hash_string, response_data.encode("utf-8"),
                            "MD5"
                        )
                        digest = hash.digest()
                        my_ans = variables.RESPONSE_511
                        my_ans[variables.DATA] = binascii.b2a_base64(
                            digest).decode("ascii")
                        send_message(self.transport, my_ans)
                        self.process_server_response(get_response(self.transport))
            except (OSError, JSONDecodeError) as e:
                LOGGER.debug(f"Connection error.", exc_info=e)
                raise ServerError("Failed to authenticate")

    def create_request(self, action: str) -> dict:
        request = {variables.TIME: time.time()}
        match action:
            case variables.PRESENCE:
                LOGGER.debug(
                    f"Message:{variables.PRESENCE} is ready for user: "
                    f"{self.username}"
                )
                request[variables.ACTION] = variables.PRESENCE
                request[variables.USER] = {
                    variables.ACCOUNT_NAME: self.username}
            case variables.EXIT:
                request[variables.ACTION] = variables.EXIT
                request[variables.ACCOUNT_NAME] = self.username
            case variables.GET_CONTACTS:
                request[variables.ACTION] = variables.GET_CONTACTS
                request[variables.USER] = self.username
            case variables.MESSAGE:
                receiver = input("Input message receiver: ")
                message_text = input("Input message to send: ")
                request[variables.ACTION] = variables.MESSAGE
                request[variables.SENDER] = self.username
                request[variables.RECEIVER] = receiver
                request[variables.ACTION] = variables.MESSAGE
                request[variables.MESSAGE_TEXT] = message_text
                LOGGER.debug(f"Configure a message dict : {request}")
                try:
                    send_message(self.transport, request)
                    LOGGER.info(f"The message is send to {receiver}")
                except Exception as e:
                    print(e)
                    LOGGER.critical("Connection is lost")
                    exit(1)
            case variables.ADD_CONTACT:
                user_id = input(f"Input new user's username: ")
                request[variables.ACTION] = variables.ADD_CONTACT
                request[variables.USER_ID] = user_id
                request[variables.USER_LOGIN] = self.username
            case variables.DEL_CONTACT:
                user_id = input(f"Input a user's username to delete: ")
                request[variables.ACTION] = variables.DEL_CONTACT
                request[variables.USER_ID] = user_id
                request[variables.USER_LOGIN] = self.username
            case variables.USERS_REQUEST:
                request[variables.ACTION] = variables.USERS_REQUEST
                request[variables.ACCOUNT_NAME] = self.username
            case variables.PUBLIC_KEY_REQUEST:
                request[variables.ACTION] = variables.PUBLIC_KEY_REQUEST
                request[variables.ACCOUNT_NAME] = self.username
        return request

    def process_server_response(self, message: dict) -> str | None:
        LOGGER.debug(f"Parse server message: {message}")
        if isinstance(message, dict):
            if variables.RESPONSE in message:
                match int(message[variables.RESPONSE]):
                    case 200:
                        return "200 : OK"
                    case 400:
                        raise ServerError(f"400: {message[variables.ERROR]}")
                    case _:
                        LOGGER.debug(
                            f"Received unknown code "
                            f"{message[variables.RESPONSE]}"
                        )

            elif (
                    variables.ACTION in message
                    and message[variables.ACTION] == variables.MESSAGE
                    and variables.SENDER in message
                    and variables.RECEIVER in message
                    and variables.MESSAGE_TEXT in message
                    and message[variables.RECEIVER] == self.username
            ):
                LOGGER.debug(
                    f"Received a message by user "
                    f"{message[variables.SENDER]}:"
                    f"{message[variables.MESSAGE_TEXT]}"
                )
                self.database.save_message(
                    message[variables.SENDER], "in",
                    message[variables.MESSAGE_TEXT]
                )
                self.new_message.emit(message[variables.SENDER])

    def contacts_list_update(self):
        LOGGER.debug(f"Contact list request for user {self.name}")
        request = self.create_request(variables.GET_CONTACTS)
        LOGGER.debug(f"Request is {request}")
        with socket_lock:
            send_message(self.transport, request)
            response = get_response(self.transport)
        LOGGER.debug(f"Response is received {response}")
        if (
                variables.RESPONSE in response
                and response[variables.RESPONSE] == 202):
            for contact in response[variables.LIST_INFO]:
                self.database.add_contact(contact)
        else:
            LOGGER.error("Failed to update contact list")

    def user_list_update(self):
        LOGGER.debug(f"Known contact list reqeust {self.username}")
        request = {
            variables.ACTION: variables.USERS_REQUEST,
            variables.TIME: time.time(),
            variables.ACCOUNT_NAME: self.username,
        }
        with socket_lock:
            send_message(self.transport, request)
            response = get_response(self.transport)
        if (
                variables.RESPONSE in response
                and response[variables.RESPONSE] == 202
        ):
            self.database.add_users(response[variables.LIST_INFO])
        else:
            LOGGER.error("Failed to update known contact list")

    def key_request(self, user: str):
        LOGGER.debug(f"Request public key for {user}")
        request = self.create_request(variables.PUBLIC_KEY_REQUEST)
        with socket_lock:
            send_message(self.transport, request)
            response = get_response(self.transport)
        if (
                variables.RESPONSE in response
                and response[variables.RESPONSE] == 511
        ):
            return response[variables.DATA]
        else:
            LOGGER.error(f"Failed to get recipient pubkey by {user}.")

    def add_contact(self):
        request = self.create_request(variables.ADD_CONTACT)
        LOGGER.debug(f"Creating a contact {request[variables.USER_ID]}")
        with socket_lock:
            send_message(self.transport, request)
            self.process_server_response(get_response(self.transport))

    def remove_contact(self):
        request = self.create_request(variables.DEL_CONTACT)
        LOGGER.debug(f"Removing a contact {request[variables.USER_ID]}")
        with socket_lock:
            send_message(self.transport, request)
            self.process_server_response(get_response(self.transport))

    def transport_shutdown(self):
        self.running = False
        message = self.create_request(variables.EXIT)
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                LOGGER.error("Failed to send message")
        LOGGER.debug("Client close connection")
        time.sleep(0.5)

    def send_message(self):
        message_dict = self.create_request(variables.MESSAGE)
        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_server_response(get_response(self.transport))
            LOGGER.info(
                f"Message has been sent to {message_dict[variables.RECEIVER]}"
            )

    def run(self):
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
                else:
                    if message:
                        LOGGER.debug(f"Received message by server: {message}")
                        self.process_server_response(message)
                finally:
                    self.transport.settimeout(5)
