from PyQt4 import QtGui, QtCore
import sys
import client
from libs.encrypt_hash import crypto
import time


class PopUpLogIn(QtGui.QWidget):
    def __init__(self, client):
        QtGui.QWidget.__init__(self)
        self.client = client
        self.init_ui()

    def set_status(self, text):
        self.status.setText(text)

    def init_ui(self):
        self.server_ip = QtGui.QLineEdit("127.0.0.1")
        self.server_ip.setPlaceholderText("IP or hostname of the server")

        self.server_port = QtGui.QLineEdit("54554")
        self.server_port.setPlaceholderText("Port number of the server")

        self.uname = QtGui.QLineEdit()
        self.uname.setPlaceholderText("Username")

        self.passwd = QtGui.QLineEdit()
        self.passwd.setPlaceholderText("Password")
        self.passwd.setEchoMode(2)

        self.login_butt = QtGui.QPushButton("&Login", self)
        self.cancel_butt = QtGui.QPushButton("&Cancel", self)
        self.status = QtGui.QLabel()

        layout = QtGui.QGridLayout()
        layout.addWidget(self.server_ip, 0, 0, 1, 2)
        layout.addWidget(self.server_port, 0, 2, 1, 2)
        layout.addWidget(self.uname, 1, 0, 1, 2)
        layout.addWidget(self.passwd, 1, 2, 1, 2)
        layout.addWidget(self.login_butt, 2, 0, 1, 1)
        layout.addWidget(self.cancel_butt, 2, 2, 1, 1)
        layout.addWidget(self.status, 3, 0, 5, 4)

        self.cancel_butt.clicked.connect(self.close)
        self.login_butt.clicked.connect(self.login)
        self.setLayout(layout)
        self.setWindowTitle("Login Panel")
        self.show()

    def login(self):
        if len(self.server_ip.text()) == 0:
            self.set_status("Empty server address")
            return False
        if len(self.server_port.text()) == 0:
            self.set_status("Empty port number")
            return False
        if int(self.server_port.text()) not in range(1, 2**16):
            self.set_status("Incorrect port number")
            return False
        if len(self.uname.text()) == 0:
            self.set_status("Please input username")
            return False
        if len(self.passwd.text()) == 0:
            self.set_status("Please input password")
            return False

        self.client.set_server(self.server_ip.text(),
                               int(self.server_port.text()))
        if not self.client.connect():
            self.set_status("Connection problems\n"
                            "Check server address and port or\ntry again later")
            return False

        uname = self.uname.text()
        passwd = crypto(self.passwd.text())
        self.set_status("asdasd")
        ok, response = self.client.log_in(uname, passwd)
        if ok:
            self.set_status("Success\n" + response.get_body())
            self.client.log_out()
            # self.cancel_butt.click()
        else:
            self.set_status("Failed\n" + response.get_body())
            # self.cancel_butt.click()
        self.login_butt.setEnabled(False)


    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.cancel_butt.animateClick()
        elif QKeyEvent.key() == QtCore.Qt.Key_Return\
            or QKeyEvent.key() == QtCore.Qt.Key_Enter:
            self.login_butt.animateClick()


if __name__ == "__main__":
    pass
