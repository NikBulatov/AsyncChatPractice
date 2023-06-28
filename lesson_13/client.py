import time
import json
import socket
import logging
from threading import Thread, Lock

from PyQt6.QtCore import QObject, pyqtSignal

from logs import client_log_config
from services.errors import *
from services import variables
from services.metaclasses import ClientVerifier
from services.parsers import parse_client_arguments
from services.common import send_message, get_response

LOGGER = logging.getLogger("client")
socket_lock = Lock()


class Client(Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, account_name):
        Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.account_name = account_name
        self.sock = None
        self.connection_init(port, ip_address)

        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                LOGGER.critical("Connection with server is lost")
                raise ServerError("Connection with server is lost")
            LOGGER.error("Timeout updating users list")
        except json.JSONDecodeError:
            LOGGER.critical("Connection with server is lost")
            raise ServerError("Connection with server is lost")
        self.running = True

    def connection_init(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)

        connected = False
        for i in range(5):
            LOGGER.info(f"Connection trying №{i + 1}")
            try:
                self.sock.connect((ip, port))
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

        LOGGER.debug('A connection has established with server')

        try:
            with socket_lock:
                send_message(self.sock,
                             self.create_request(variables.PRESENCE))
                self.process_server_response(get_response(self.sock))
        except (OSError, json.JSONDecodeError):
            LOGGER.critical('Потеряно соединение с сервером!')
            raise ServerError('Потеряно соединение с сервером!')

        LOGGER.info('Соединение с сервером успешно установлено.')

    def create_request(self, action: str) -> dict:
        request = {variables.TIME: time.time()}
        match action:
            case variables.PRESENCE:
                LOGGER.debug(
                    f"Message:{variables.PRESENCE} is ready for user: {self.account_name}")
                request[variables.ACTION] = variables.PRESENCE
                request[variables.USER] = {
                    variables.ACCOUNT_NAME: self.account_name}
            case variables.EXIT:
                request[variables.ACTION] = variables.EXIT
                request[variables.ACCOUNT_NAME] = self.account_name
            case variables.GET_CONTACTS:
                request[variables.ACTION] = variables.GET_CONTACTS
                request[variables.USER_LOGIN] = self.account_name
            case variables.MESSAGE:
                receiver = input("Input message receiver: ")
                message_text = input("Input message to send: ")
                request[variables.ACTION] = variables.MESSAGE
                request[variables.SENDER] = self.account_name
                request[variables.RECEIVER] = receiver
                request[variables.ACTION] = variables.MESSAGE
                request[variables.MESSAGE_TEXT] = message_text
                LOGGER.debug(f"Configure a message dict : {request}")
                try:
                    send_message(self.sock, request)
                    LOGGER.info(f"The message is send to {receiver}")
                except Exception as e:
                    print(e)
                    LOGGER.critical("Connection is lost")
                    exit(1)
            case variables.ADD_CONTACT:
                user_id = input(f"Input new user's username: ")
                request[variables.ACTION] = variables.ADD_CONTACT
                request[variables.USER_ID] = user_id
                request[variables.USER_LOGIN] = self.account_name
            case variables.DEL_CONTACT:
                user_id = input(f"Input a user's username to delete: ")
                request[variables.ACTION] = variables.DEL_CONTACT
                request[variables.USER_ID] = user_id
                request[variables.USER_LOGIN] = self.account_name
        return request

    def process_server_response(self, message):
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
                            f"Received unknown code {message[variables.RESPONSE]}")

            elif variables.ACTION in message \
                    and message[variables.ACTION] == variables.MESSAGE \
                    and variables.SENDER in message \
                    and variables.RECEIVER in message \
                    and variables.MESSAGE_TEXT in message \
                    and message[variables.RECEIVER] == self.account_name:
                LOGGER.debug(
                    f"Received a message by user "
                    f"{message[variables.SENDER]}:{message[variables.MESSAGE_TEXT]}")
                self.database.save_message(message[variables.SENDER], 'in',
                                           message[variables.MESSAGE_TEXT])
                self.new_message.emit(message[variables.SENDER])

    # Функция обновляющая контакт - лист с сервера
    def contacts_list_update(self):
        LOGGER.debug(f"Запрос контакт листа для пользователся {self.name}")
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.account_name
        }
        LOGGER.debug(f'Сформирован запрос {req}')
        with socket_lock:
            send_message(self.sock, req)
            ans = get_response(self.sock)
        LOGGER.debug(f'Получен ответ {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            LOGGER.error('Не удалось обновить список контактов.')

    # Функция обновления таблицы известных пользователей.
    def user_list_update(self):
        LOGGER.debug(
            f'Запрос списка известных пользователей {self.account_name}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }
        with socket_lock:
            send_message(self.sock, req)
            ans = get_response(self.sock)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            LOGGER.error('Не удалось обновить список известных пользователей.')

    def add_contact(self):
        request = self.create_request(variables.ADD_CONTACT)
        LOGGER.debug(f'Creating a contact {request[variables.USER_ID]}')
        with socket_lock:
            send_message(self.sock, request)
            self.process_server_response(get_response(self.sock))

    def remove_contact(self):
        request = self.create_request(variables.DEL_CONTACT)
        LOGGER.debug(f'Removing a contact {request[variables.USER_ID]}')
        with socket_lock:
            send_message(self.sock, request)
            self.process_server_response(get_response(self.sock))

    def transport_shutdown(self):
        self.running = False
        message = self.create_request(variables.EXIT)
        with socket_lock:
            try:
                send_message(self.sock, message)
            except OSError:
                LOGGER.error("Failed to send message")
        LOGGER.debug('Client close connection')
        time.sleep(0.5)

    def send_message(self):
        message_dict = self.create_request(variables.MESSAGE)
        with socket_lock:
            send_message(self.sock, message_dict)
            self.process_server_response(get_response(self.sock))
            LOGGER.info(
                f"Message has been sent to {message_dict[variables.RECEIVER]}")

    def run(self):
        LOGGER.debug("Start proccess - message received by server.")
        while self.running:
            time.sleep(.75)
            with socket_lock:
                try:
                    self.sock.settimeout(0.5)
                    message = get_response(self.sock)
                except OSError as err:
                    if err.errno:
                        LOGGER.critical("Connection is lost")
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError, TypeError):
                    LOGGER.debug("Connection is lost")
                    self.running = False
                    self.connection_lost.emit()
                else:
                    LOGGER.debug(f'Received a message by server: {message}')
                    self.process_server_response(message)
                finally:
                    self.sock.settimeout(5)
