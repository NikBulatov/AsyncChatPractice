from PyQt6.QtWidgets import QDialog, QPushButton, QTableView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt


class StartWindow(QDialog):
    def __init__(self, database):
        super().__init__()

        self.database = database
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Client statistics")
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.close_button = QPushButton("Close", self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.stat_table = QTableView(self)
        self.stat_table.move(10, 10)
        self.stat_table.setFixedSize(580, 620)

        self.create_stat_model()

    def create_stat_model(self):
        stat_list = self.database.message_history()

        lst = QStandardItemModel()
        lst.setHorizontalHeaderLabels(
            ["Client username", "Last login",
             "Messages send", "Messages received"]
        )
        for row in stat_list:
            user, last_seen, sent, received = row
            user = QStandardItem(user)
            user.setEditable(False)
            last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
            last_seen.setEditable(False)
            sent = QStandardItem(str(sent))
            sent.setEditable(False)
            received = QStandardItem(str(received))
            received.setEditable(False)
            lst.appendRow([user, last_seen, sent, received])
        self.stat_table.setModel(lst)
        self.stat_table.resizeColumnsToContents()
        self.stat_table.resizeRowsToContents()
