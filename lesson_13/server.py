import configparser
import logging
import os
import sys
from threading import Thread, Lock
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
from logs import server_log_config
from server.server_ui import (MainWindow, gui_create_model, HistoryWindow,
                              create_stat_model, ConfigWindow)
from server.server_models import ServerStorage
from services import variables
from services.descriptors import Port
from services.metaclasses import ServerVerifier
from services.parsers import parse_server_arguments
from services.common import get_response, send_message

LOGGER = logging.getLogger('server')

new_connection = False
lock_flag = Lock()


class Server(Thread, metaclass=ServerVerifier):
    port = Port()

    def __init__(self,
                 listen_address: str,
                 listen_port: int,
                 database: ServerStorage):
        self.addr = listen_address
        self.port = listen_port
        self.database = database
        self.clients = []
        self.messages = []
        self.names = {}
        self.sock = None
        super().__init__()

    def init_socket(self):
        LOGGER.info(
            f"Server started, listening port: {self.port}, "
            f"listening address: {self.addr}. "
            f"If no address, listen all connections")

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
                    recv_data, send_data, errors = select(self.clients,
                                                          self.clients, [], 0)
            except OSError as e:
                LOGGER.error(f'Error working with sockets: {e}')

            if recv_data:
                for client_with_message in recv_data:
                    try:
                        self.request_handler(
                            get_response(client_with_message),
                            client_with_message)
                    except OSError:
                        LOGGER.info(
                            f"Client {client_with_message.getpeername()} "
                            f"close connection")
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
                    self.process_message(message, send_data)
                except (ConnectionAbortedError, ConnectionError,
                        ConnectionResetError,
                        ConnectionRefusedError):
                    LOGGER.info(
                        f"Connection with client {message[variables.RECEIVER]}"
                        f" is lost")
                    self.clients.remove(
                        self.names[message[variables.RECEIVER]])
                    self.database.user_logout(message[variables.RECEIVER])
                    del self.names[message[variables.RECEIVER]]
                    with lock_flag:
                        new_connection = True
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
        global new_connection
        LOGGER.debug(f"Process client message: {request}")
        if variables.ACTION in request and variables.TIME in request:
            match request[variables.ACTION]:
                case variables.PRESENCE:
                    if variables.USER in request:
                        name = request[variables.USER][variables.ACCOUNT_NAME]
                        if name in self.names.keys() and self.names.get(name):
                            response = variables.RESPONSE_400
                            response[variables.ERROR] = \
                                "Current username is used"
                            send_message(client, response)
                            self.clients.remove(client)
                            client.close()
                        else:
                            self.names[name] = client
                            client_ip, client_port = client.getpeername()
                            self.database.user_login(name, client_ip,
                                                     client_port)
                            send_message(client, variables.RESPONSE_200)
                            with lock_flag:
                                new_connection = True
                case variables.MESSAGE:
                    if (variables.SENDER in request
                            and variables.MESSAGE_TEXT in request):
                        if variables.RECEIVER in request:
                            self.messages.append(request)
                            self.database.process_message(
                                request[variables.SENDER],
                                request[variables.RECEIVER])
                            send_message(client, variables.RESPONSE_200)
                        else:
                            response = variables.RESPONSE_400
                            response[variables.ERROR] = \
                                "User is not registred on server."
                            send_message(client, response)
                case variables.EXIT:
                    if variables.ACCOUNT_NAME in request:
                        self.database.user_logout(
                            request[variables.ACCOUNT_NAME])
                        LOGGER.info(
                            f"Client {request[variables.ACCOUNT_NAME]} "
                            f"disconnected correctly")
                        removed = self.names.pop(
                            request[variables.ACCOUNT_NAME], None)
                        self.clients.remove(removed)
                        removed.close()
                        del removed
                        with lock_flag:
                            new_connection = True
                case variables.GET_CONTACTS:
                    if request[variables.USER_LOGIN] in self.names.keys():
                        response = {variables.RESPONSE: 202,
                                    variables.ALERT: self.database.get_contacts(
                                        request[variables.USER])}
                        send_message(client, response)
                    else:
                        response = variables.RESPONSE_404
                        response[variables.ERROR] = "Not authorized"
                        send_message(client, response)
                case variables.ADD_CONTACT:
                    if request[variables.USER_LOGIN] in self.names.keys():
                        if not request[variables.USER_ID] in self.names.keys():
                            self.database.add_contact(
                                request[variables.USER],
                                request[variables.ACCOUNT_NAME])
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
                            self.database.remove_contact(
                                request[variables.USER],
                                request[variables.ACCOUNT_NAME])
                            removed = self.names[request[variables.USER_ID]]
                            self.names.pop(request[variables.USER_ID])
                        except KeyError:
                            response = variables.RESPONSE_400
                            response[variables.ERROR] = \
                                "Current user_id doesn't exist"
                        else:
                            if removed:
                                self.clients.remove(removed)
                                removed.close()
                            response = variables.RESPONSE_200
                        finally:
                            del removed
                        send_message(client, response)
        else:
            response = variables.RESPONSE_400
            response[variables.ERROR] = "Invalid request"
            send_message(client, response)


def config_load():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(variables.SERVER_CONFIG)
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section("SETTINGS")
        config.set("SETTINGS", "Default_port", str(variables.DEFAULT_PORT))
        config.set("SETTINGS", "Listen_Address", "")
        config.set("SETTINGS", "Database_path", "")
        config.set("SETTINGS", "Database_file", "server_database.db3")
        return config


def main():
    config = config_load()
    listen_address, listen_port = parse_server_arguments()
    database = ServerStorage(os.path.join(config["SETTINGS"]["Database_path"],
                                          config["SETTINGS"]["Database_file"]))

    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.run()

    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.statusBar().showMessage("Server Working")
    main_window.active_clients_table.setModel(gui_create_model(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(
                gui_create_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with lock_flag:
                new_connection = False

    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(config["SETTINGS"]["Database_path"])
        config_window.db_file.insert(config["SETTINGS"]["Database_file"])
        config_window.port.insert(config["SETTINGS"]["Default_port"])
        config_window.ip.insert(config["SETTINGS"]["Listen_Address"])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        config["SETTINGS"]["Database_path"] = config_window.db_path.text()
        config["SETTINGS"]["Database_file"] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, "Error", "Port value is int type")
        else:
            config["SETTINGS"]["Listen_Address"] = config_window.ip.text()
            if 1023 < port < 65536:
                config["SETTINGS"]["Default_port"] = str(port)
                dir_path = os.path.dirname(os.path.realpath(__file__))
                with open(variables.SERVER_CONFIG, 'w') as conf:
                    config.write(conf)
                    message.information(config_window, "OK",
                                        "Setting saved successfully!")
            else:
                message.warning(config_window, "Error",
                                "Port valid values: 1024 - 65536")

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    server_app.exec()


if __name__ == "__main__":
    main()
