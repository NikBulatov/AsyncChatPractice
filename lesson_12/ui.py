import sys

from PyQt6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout,
                             QWidget, QPushButton, QTableWidget, QGridLayout,
                             QGroupBox, QSpinBox, QLineEdit, QVBoxLayout,
                             QLabel, QBoxLayout)


def init_table(columns: int, rows: int,
               headers: list[str]) -> QTableWidget:
    table = QTableWidget()
    table.setColumnCount(columns)
    table.setRowCount(rows)
    table.setHorizontalHeaderLabels(headers)
    return table


class ClientTableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Client List")
        self.setMinimumSize(500, 400)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        headers = ["ID", "Username", "Last Login"]
        self.table = init_table(len(headers), 1, headers)
        self.grid_layout.addWidget(self.table, 0, 0)


class StatisticWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Statistic")
        self.setMinimumSize(600, 400)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        headers = ["ID", "Username", "Last Login", "IP address", "Port"]
        self.table = init_table(len(headers), 1, headers)
        self.grid_layout.addWidget(self.table, 0, 0)


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")
        layout = QHBoxLayout()
        socket_layout = self.socket_settings_init()
        db_layout = self.db_settings_init()
        layout.addWidget(socket_layout)
        layout.addWidget(db_layout)
        self.setLayout(layout)

    def socket_settings_init(self):
        server_settings = QGroupBox("Server settings")

        port_label = QLabel("Port")
        port_value = QSpinBox()

        address_label = QLabel("Listen address")
        listen_address_value = QLineEdit()

        button = QPushButton("OK")  # need signal

        box = QVBoxLayout()
        port_box = QHBoxLayout()
        address_box = QHBoxLayout()

        address_box.addWidget(address_label)
        address_box.addWidget(listen_address_value)

        port_box.addWidget(port_label)
        port_box.addWidget(port_value)

        box.addLayout(address_box)
        box.addLayout(port_box)
        box.addWidget(button)

        server_settings.setLayout(box)
        return server_settings

    def db_settings_init(self):
        db_settings = QGroupBox("Database connection settings")

        # labels
        host_label = QLabel("Host")
        port_label = QLabel("Port")
        db_label = QLabel("Database")
        login_label = QLabel("Login")
        password_label = QLabel("Password")

        # value_keepers
        host_value = QLineEdit()
        port_value = QSpinBox()
        db_value = QLineEdit()
        login_value = QLineEdit()
        password_value = QLineEdit()
        password_value.setEchoMode(QLineEdit.EchoMode.Password)

        button = QPushButton("OK")  # need signal

        # boxes
        box = QVBoxLayout()
        host_box = QHBoxLayout()
        host_box.addWidget(host_label)
        host_box.addWidget(host_value)

        port_box = QHBoxLayout()
        port_box.addWidget(port_label)
        port_box.addWidget(port_value)

        db_box = QHBoxLayout()
        db_box.addWidget(db_label)
        db_box.addWidget(db_value)

        login_box = QHBoxLayout()
        login_box.addWidget(login_label)
        login_box.addWidget(login_value)

        password_box = QHBoxLayout()
        password_box.addWidget(password_label)
        password_box.addWidget(password_value)

        for item in host_box, port_box, db_box, login_box, password_box:
            box.addLayout(item)

        box.addWidget(button)

        db_settings.setLayout(box)
        return db_settings


class ButtonGroup:
    def __init__(self):
        self.client_list_button = QPushButton("Client List")
        self.settings_button = QPushButton("Settings")
        self.statistic_button = QPushButton("Statistics")

        self.client_list_button.clicked.connect(self.client_list_button_click)
        self.settings_button.clicked.connect(self.settings_button_click)
        self.statistic_button.clicked.connect(self.statistic_button_click)

    def client_list_button_click(self):
        print("Client list button clicked")
        self.client_list_window = ClientTableWindow()
        self.client_list_window.show()

    def settings_button_click(self):
        print("Settings button clicked")
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def statistic_button_click(self):
        print("Statistics button clicked")
        self.statistic_window = StatisticWindow()
        self.statistic_window.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admin App")

        self.buttons = ButtonGroup()
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.buttons.settings_button)
        self.layout.addWidget(self.buttons.statistic_button)
        self.layout.addWidget(self.buttons.client_list_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()
