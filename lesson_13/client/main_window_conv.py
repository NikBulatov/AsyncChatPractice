# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainClientWindow(object):
    def setupUi(self, MainClientWindow):
        MainClientWindow.setObjectName("MainClientWindow")
        MainClientWindow.resize(756, 534)
        MainClientWindow.setMinimumSize(QtCore.QSize(756, 534))
        self.centralwidget = QtWidgets.QWidget(parent=MainClientWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_contacts = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_contacts.setGeometry(QtCore.QRect(10, 0, 101, 16))
        self.label_contacts.setObjectName("label_contacts")
        self.btn_add_contact = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btn_add_contact.setGeometry(QtCore.QRect(10, 450, 121, 31))
        self.btn_add_contact.setObjectName("btn_add_contact")
        self.btn_remove_contact = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btn_remove_contact.setGeometry(QtCore.QRect(140, 450, 121, 31))
        self.btn_remove_contact.setObjectName("btn_remove_contact")
        self.label_history = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_history.setGeometry(QtCore.QRect(300, 0, 391, 21))
        self.label_history.setObjectName("label_history")
        self.text_message = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.text_message.setGeometry(QtCore.QRect(300, 360, 441, 71))
        self.text_message.setObjectName("text_message")
        self.label_new_message = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_new_message.setGeometry(QtCore.QRect(300, 330, 171, 16))
        self.label_new_message.setObjectName("label_new_message")
        self.list_contacts = QtWidgets.QListView(parent=self.centralwidget)
        self.list_contacts.setGeometry(QtCore.QRect(10, 20, 251, 411))
        self.list_contacts.setObjectName("list_contacts")
        self.list_messages = QtWidgets.QListView(parent=self.centralwidget)
        self.list_messages.setGeometry(QtCore.QRect(300, 20, 441, 301))
        self.list_messages.setObjectName("list_messages")
        self.btn_send = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btn_send.setGeometry(QtCore.QRect(610, 450, 131, 31))
        self.btn_send.setObjectName("btn_send")
        self.btn_clear = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btn_clear.setGeometry(QtCore.QRect(460, 450, 131, 31))
        self.btn_clear.setObjectName("btn_clear")
        MainClientWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainClientWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 756, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(parent=self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_2.setObjectName("menu_2")
        MainClientWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(parent=MainClientWindow)
        self.statusBar.setObjectName("statusBar")
        MainClientWindow.setStatusBar(self.statusBar)
        self.menu_exit = QtGui.QAction(parent=MainClientWindow)
        self.menu_exit.setObjectName("menu_exit")
        self.menu_add_contact = QtGui.QAction(parent=MainClientWindow)
        self.menu_add_contact.setObjectName("menu_add_contact")
        self.menu_del_contact = QtGui.QAction(parent=MainClientWindow)
        self.menu_del_contact.setObjectName("menu_del_contact")
        self.menu.addAction(self.menu_exit)
        self.menu_2.addAction(self.menu_add_contact)
        self.menu_2.addAction(self.menu_del_contact)
        self.menu_2.addSeparator()
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())

        self.retranslateUi(MainClientWindow)
        self.btn_clear.clicked.connect(self.text_message.clear) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainClientWindow)

    def retranslateUi(self, MainClientWindow):
        _translate = QtCore.QCoreApplication.translate
        MainClientWindow.setWindowTitle(_translate("MainClientWindow", "Chat app alpha release"))
        self.label_contacts.setText(_translate("MainClientWindow", "Contact List:"))
        self.btn_add_contact.setText(_translate("MainClientWindow", "Add contact"))
        self.btn_remove_contact.setText(_translate("MainClientWindow", "Remove contact"))
        self.label_history.setText(_translate("MainClientWindow", "Message history:"))
        self.label_new_message.setText(_translate("MainClientWindow", "Input new message:"))
        self.btn_send.setText(_translate("MainClientWindow", "Send message"))
        self.btn_clear.setText(_translate("MainClientWindow", "Clear"))
        self.menu.setTitle(_translate("MainClientWindow", "File"))
        self.menu_2.setTitle(_translate("MainClientWindow", "Contacts"))
        self.menu_exit.setText(_translate("MainClientWindow", "Exit"))
        self.menu_add_contact.setText(_translate("MainClientWindow", "Add contact"))
        self.menu_del_contact.setText(_translate("MainClientWindow", "Delete contact"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainClientWindow = QtWidgets.QMainWindow()
    ui = Ui_MainClientWindow()
    ui.setupUi(MainClientWindow)
    MainClientWindow.show()
    sys.exit(app.exec())
