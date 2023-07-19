from PyQt6.QtWidgets import (
    QDialog,
    QPushButton,
    QLineEdit,
    QApplication,
    QLabel
)


class UserNameDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.ok_pressed = False

        self.setWindowTitle("Hello!")
        self.setFixedSize(175, 135)

        self.label = QLabel("Input user name:", self)
        self.label.move(10, 10)
        self.label.setFixedSize(150, 10)

        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(154, 20)
        self.client_name.move(10, 30)

        self.label_passwd = QLabel("Input password:", self)
        self.label_passwd.move(10, 55)
        self.label_passwd.setFixedSize(150, 15)

        self.client_password = QLineEdit(self)
        self.client_password.setFixedSize(154, 20)
        self.client_password.move(10, 75)
        self.client_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_ok = QPushButton("Start", self)
        self.btn_ok.move(10, 105)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton("Exit", self)
        self.btn_cancel.move(90, 105)
        self.btn_cancel.clicked.connect(QApplication.exit)
        self.show()

    def click(self):
        if self.client_name.text() and self.client_password.text():
            self.ok_pressed = True
            QApplication.exit()


if __name__ == "__main__":
    app = QApplication([])
    dial = UserNameDialog()
    app.exec()
