import os
import sys
import logging
from Crypto.PublicKey import RSA
from PyQt6.QtWidgets import QApplication, QMessageBox

from services.errors import ServerError
from client.helpers import parse_client_args
from client.client_models import ClientDatabase
from client.transport import Client
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog

LOGGER = logging.getLogger("client")

if __name__ == "__main__":
    server_address, server_port, client_name, client_password = parse_client_args()
    app = QApplication(sys.argv)

    start_dialog = UserNameDialog()
    if not client_name or not client_password:
        app.exec()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_password = start_dialog.client_password.text()
        else:
            exit(0)

    LOGGER.info(
        f"""Run client with:
        - Server ip: {server_address},
        - Port: {server_port},
        - Username: {client_name}"""
    )

    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f"{client_name}.key")
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, "wb") as key:
            key.write(keys.export_key())
    else:
        with open(key_file, "rb") as key:
            keys = RSA.import_key(key.read())

    keys.publickey().export_key()
    database = ClientDatabase(client_name)
    try:
        transport = Client(
            server_port, server_address, database, client_name, client_password, keys
        )
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, "Server error", error.text)
        exit(1)
    transport.daemon = True
    transport.start()

    del start_dialog

    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f"Messanger alpha release - {client_name}")
    app.exec()

    transport.transport_shutdown()
    transport.join()
