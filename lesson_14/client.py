import sys
import logging
from PyQt6.QtWidgets import QApplication

from logs import client_log_config
from services.errors import ServerError
from services.client_helpers import parse_client_args
from client.client_models import ClientDatabase
from client.transport import Client
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog

LOGGER = logging.getLogger("client")

if __name__ == '__main__':
    server_address, server_port, client_name = parse_client_args()

    client_app = QApplication(sys.argv)

    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    LOGGER.info(
        f"""Run client with:
        - Server ip: {server_address},
        - Port: {server_port},
        - Username: {client_name}""")

    database = ClientDatabase(client_name)

    try:
        transport = Client(server_port, server_address, database, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    transport.daemon = True
    transport.start()

    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f"Chat app alpha release - {client_name}")
    client_app.exec()

    transport.transport_shutdown()
    transport.join()
