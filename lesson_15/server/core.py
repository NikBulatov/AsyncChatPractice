import configparser
import hmac
import logging
import os
import sys
import binascii
from threading import Thread, Lock
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from .server_models import ServerStorage

sys.path.append("../")
from logs import server_log_config

from services import variables
from services.descriptors import Port
from services.metaclasses import ServerVerifier
from services.common import get_response, send_message, login_required

LOGGER = logging.getLogger("server")

new_connection = False
lock_flag = Lock()


class Server(Thread, metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_address: str, listen_port: int, database: ServerStorage):
        self.addr = listen_address
        self.port = listen_port
        self.database = database
        self.clients = []
        self.messages = []
        self.names = {}
        self.sock = None
        self.listen_sockets = None
        self.error_sockets = None
        self.running = True
        super().__init__()

    def init_socket(self):
        LOGGER.info(
            f"Server started, listening port: {self.port}, "
            f"listening address: {self.addr}. "
            f"If no address, listen all connections"
        )

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((self.addr, self.port))
        self.sock.settimeout(0.5)
        self.sock.listen()

    def run(self):
        global new_connection
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
                    recv_data, send_data, errors = select(
                        self.clients, self.clients, [], 0
                    )
            except OSError as e:
                LOGGER.error(f"Error working with sockets: {e}")

            if recv_data:
                for client_with_message in recv_data:
                    try:
                        self.request_handler(
                            get_response(client_with_message), client_with_message
                        )
                    except OSError:
                        LOGGER.info(
                            f"Client {client_with_message.getpeername()} "
                            f"close connection"
                        )
                        for name in self.names:
                            if self.names.get(name) == client_with_message:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client_with_message)
                        with lock_flag:
                            new_connection = True

            for message in self.messages:
                try:
                    self.process_message(message)
                except (
                    ConnectionAbortedError,
                    ConnectionError,
                    ConnectionResetError,
                    ConnectionRefusedError,
                ):
                    LOGGER.info(
                        f"Connection with client {message[variables.RECEIVER]}"
                        f" is lost"
                    )
                    self.clients.remove(self.names[message[variables.RECEIVER]])
                    self.database.user_logout(message[variables.RECEIVER])
                    del self.names[message[variables.RECEIVER]]
                    with lock_flag:
                        new_connection = True
            self.messages.clear()

    def remove_client(self, client: socket):
        LOGGER.info(f"Client {client.getpeername()} disconnect")
        for name in self.names:
            if self.names[name] == client:
                self.database.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()

    def process_message(self, message: dict) -> None:
        if message[variables.RECEIVER] in self.names:
            if self.names[message[variables.RECEIVER]] in self.listen_sockets:
                try:
                    send_message(self.names[message[variables.RECEIVER]], message)
                    LOGGER.info(
                        f"Message's send to {message[variables.RECEIVER]} "
                        f"by {message[variables.SENDER]}."
                    )
                except OSError:
                    self.remove_client(message[variables.RECEIVER])
            else:
                LOGGER.error(
                    f"Connection with client {message[variables.RECEIVER]} "
                    f"was lost. Connection is closed. Message isn't send"
                )
                self.remove_client(self.names[message[variables.RECEIVER]])
        else:
            LOGGER.error(
                f'User "{message[variables.RECEIVER]}" isn\'t registered,'
                f" message isn't send"
            )

    @login_required
    def request_handler(self, request: dict, client: socket):
        LOGGER.debug(f"Process client message: {request}")
        if variables.ACTION in request and variables.TIME in request:
            match request[variables.ACTION]:
                case variables.PRESENCE:
                    self.authorize_user(request, client)
                case variables.MESSAGE:
                    if (
                        variables.RECEIVER in request
                        and variables.SENDER in request
                        and variables.MESSAGE_TEXT in request
                        and self.names[request[variables.SENDER]] == client
                    ):
                        if request[variables.RECEIVER] in self.names:
                            self.database.process_message(
                                request[variables.SENDER], request[variables.RECEIVER]
                            )
                            self.process_message(request)
                            try:
                                send_message(client, variables.RESPONSE_200)
                            except OSError:
                                self.remove_client(client)
                    else:
                        response = variables.RESPONSE_400
                        response[
                            variables.ERROR
                        ] = "Current user isn't registred on server"
                        try:
                            send_message(client, response)
                        except OSError:
                            pass
                case variables.EXIT:
                    if (
                        variables.ACCOUNT_NAME in request
                        and self.names[request[variables.ACCOUNT_NAME]] == client
                    ):
                        self.remove_client(client)
                case variables.GET_CONTACTS:
                    if (
                        request[variables.USER_LOGIN] in self.names.keys()
                        and variables.USER in request
                        and self.names[request[variables.USER]] == client
                    ):
                        response = variables.RESPONSE_202
                        response[variables.LIST_INFO] = self.database.get_contacts(
                            request[variables.USER]
                        )
                        try:
                            send_message(client, response)
                        except OSError:
                            self.remove_client(client)
                case variables.ADD_CONTACT:
                    if (
                        variables.ACCOUNT_NAME in request
                        and variables.USER in request
                        and self.names[request[variables.USER]] == client
                    ):
                        self.database.add_contact(
                            request[variables.USER], request[variables.ACCOUNT_NAME]
                        )
                        try:
                            send_message(client, variables.RESPONSE_200)
                        except OSError:
                            self.remove_client(client)
                case variables.DEL_CONTACT:
                    if request[variables.USER_LOGIN] in self.names.keys():
                        self.database.remove_contact(
                            request[variables.USER], request[variables.ACCOUNT_NAME]
                        )
                        try:
                            send_message(client, variables.RESPONSE_200)
                        except OSError:
                            self.remove_client(client)
                case variables.USERS_REQUEST:
                    if (
                        variables.ACCOUNT_NAME in request
                        and self.names[request[variables.ACCOUNT_NAME]] == client
                    ):
                        response = variables.RESPONSE_202
                        response[variables.LIST_INFO] = [
                            user[0] for user in self.database.users_list()
                        ]
                        try:
                            send_message(client, response)
                        except OSError:
                            self.remove_client(client)
                case variables.PUBLIC_KEY_REQUEST:
                    if variables.ACCOUNT_NAME in request:
                        response = variables.RESPONSE_511
                        response[variables.DATA] = self.database.get_pubkey(
                            request[variables.ACCOUNT_NAME]
                        )
                        if response[variables.DATA]:
                            try:
                                send_message(client, response)
                            except OSError:
                                self.remove_client(client)
                        else:
                            response = variables.RESPONSE_400
                            response[
                                variables.ERROR
                            ] = "Pubkey doesn't exist from current user"
                            try:
                                send_message(client, response)
                            except OSError:
                                self.remove_client(client)
        else:
            response = variables.RESPONSE_400
            response[variables.ERROR] = "Invalid request"
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)

    def authorize_user(self, request: dict, sock: socket):
        LOGGER.debug(f"Start auth process for {request[variables.USER]}")
        if request[variables.USER][variables.ACCOUNT_NAME] in self.names.keys():
            response = variables.RESPONSE_400
            response[variables.ERROR] = "Current username exists"
            try:
                LOGGER.debug(f"Username busy, sending {response}")
                send_message(sock, response)
            except OSError:
                LOGGER.debug("OS Error")
            self.clients.remove(sock)
            sock.close()
        elif not self.database.check_user(
            request[variables.USER][variables.ACCOUNT_NAME]
        ):
            response = variables.RESPONSE_400
            response[variables.ERROR] = "Current user is not registered"
            try:
                LOGGER.debug(f"Unknown username, sending {response}")
                send_message(sock, response)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        else:
            LOGGER.debug("Correct username, starting passwd check.")
            message_auth = variables.RESPONSE_511
            random_str = binascii.hexlify(os.urandom(64))
            message_auth[variables.DATA] = random_str.decode("ascii")
            hash = hmac.new(
                self.database.get_hash(request[variables.USER][variables.ACCOUNT_NAME]),
                random_str,
                "MD5",
            )
            digest = hash.digest()
            LOGGER.debug(f"Auth message = {message_auth}")
            try:
                send_message(sock, message_auth)
                response = get_response(sock)
            except OSError as e:
                LOGGER.debug("Error in auth, data:", exc_info=e)
                sock.close()
                return
            client_digest = binascii.a2b_base64(response[variables.DATA])
            if (
                variables.RESPONSE in response
                and response[variables.RESPONSE] == 511
                and hmac.compare_digest(digest, client_digest)
            ):
                self.names[request[variables.USER][variables.ACCOUNT_NAME]] = sock
                client_ip, client_port = sock.getpeername()
                try:
                    send_message(sock, variables.RESPONSE_200)
                except OSError:
                    self.remove_client(request[variables.USER][variables.ACCOUNT_NAME])
                self.database.user_login(
                    request[variables.USER][variables.ACCOUNT_NAME],
                    client_ip,
                    client_port,
                    request[variables.USER][variables.PUBLIC_KEY],
                )
            else:
                response = variables.RESPONSE_400
                response[variables.ERROR] = "Incorrect password"
                try:
                    send_message(sock, response)
                except OSError:
                    pass
                self.clients.remove(sock)
                sock.close()

    def service_update_lists(self):
        for client in self.names:
            try:
                send_message(self.names[client], variables.RESPONSE_205)
            except OSError:
                self.remove_client(self.names[client])
