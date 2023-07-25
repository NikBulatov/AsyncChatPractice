import sys
import os
import argparse
import logging
import configparser
from PyQt6.QtWidgets import QApplication
from logs import server_log_config
from services import variables
from services.common import log
from server.core import Server
from server.server_models import ServerStorage
from server.main_window import MainWindow

LOGGER = logging.getLogger("server")


@log
def arg_parser(default_port: str, default_address: str) -> tuple:
    LOGGER.debug(f"Initialization of CLI argument parser : {sys.argv}")
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", default=default_port, type=int, nargs="?")
    parser.add_argument("-a", default=default_address, nargs="?")
    parser.add_argument("--no_gui", action="store_true")
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    gui_flag = namespace.no_gui
    LOGGER.debug("Arguments successfully loaded")
    return listen_address, listen_port, gui_flag


@log
def config_load() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{variables.SERVER_CONFIG}")
    if "SETTINGS" in config:
        return config
    else:
        config.add_section("SETTINGS")
        config.set("SETTINGS", "Default_port", str(variables.DEFAULT_PORT))
        config.set("SETTINGS", "Listen_Address", "")
        config.set("SETTINGS", "Database_path", "")
        config.set("SETTINGS", "Database_file", "server_database.db3")
        return config


@log
def main():
    config = config_load()

    listen_address, listen_port, gui_flag = arg_parser(
        config["SETTINGS"]["Default_port"], config["SETTINGS"]["Listen_Address"]
    )

    database = ServerStorage(
        os.path.join(
            config["SETTINGS"]["Database_path"], config["SETTINGS"]["Database_file"]
        )
    )

    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    if gui_flag:
        while True:
            command = input("Input 'exit' to terminate the server")
            if command == "exit":
                server.running = False
                server.join()
                break

    else:
        server_app = QApplication(sys.argv)
        main_window = MainWindow(database, server, config)
        server_app.exec()
        server.running = False


if __name__ == "__main__":
    main()
