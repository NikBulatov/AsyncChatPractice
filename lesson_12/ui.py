import sys

from PyQt6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout,
                             QWidget, QPushButton, QTableWidget, QGridLayout)


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
        self.table = self.init_table(len(headers), 1, headers)
        self.grid_layout.addWidget(self.table, 0, 0)

    @staticmethod
    def init_table(columns: int, rows: int,
                   headers: list[str]) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(columns)
        table.setRowCount(rows)
        table.setHorizontalHeaderLabels(headers)
        return table


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
        self.table = self.init_table(len(headers), 1, headers)
        self.grid_layout.addWidget(self.table, 0, 0)

    @staticmethod
    def init_table(columns: int, rows: int,
                   headers: list[str]) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(columns)
        table.setRowCount(rows)
        table.setHorizontalHeaderLabels(headers)
        return table


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")


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
