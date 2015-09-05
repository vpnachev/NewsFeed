from PyQt4 import QtGui, QtCore
import sys
import client
from libs.encrypt_hash import crypto
import time


class PopUpLogIn(QtGui.QWidget):
    def __init__(self, client, p=None):
        QtGui.QWidget.__init__(self, p)
        self.__logedin = False
        self.client = client
        self.init_ui()

    def closeEvent(self, QCloseEvent):
        if self.is_loged_in():
            self.client.log_out()
        QCloseEvent.accept()

    def set_status(self, text):
        self.status.setText(text)

    def is_loged_in(self):
        return self.__logedin

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

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.server_ip, 0, 0, 1, 2)
        self.layout.addWidget(self.server_port, 0, 2, 1, 2)
        self.layout.addWidget(self.uname, 1, 0, 1, 2)
        self.layout.addWidget(self.passwd, 1, 2, 1, 2)
        self.layout.addWidget(self.login_butt, 2, 0, 1, 1)
        self.layout.addWidget(self.cancel_butt, 2, 2, 1, 1)
        self.layout.addWidget(self.status, 3, 0, 5, 4)

        self.cancel_butt.clicked.connect(self.close)
        self.login_butt.clicked.connect(self.login)
        self.setGeometry(0, 0, 400, 300)
        self.setLayout(self.layout)
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
                            "Check server address and port or try again later")
            return False

        uname = self.uname.text()
        passwd = crypto(self.passwd.text())
        self.set_status("asdasd")
        self.__logedin, response = self.client.log_in(uname, passwd)
        if self.is_loged_in():
            self.set_status("Success\n" + response.get_body())
            self.uname.setParent(None)
            self.passwd.setParent(None)
            self.server_port.setParent(None)
            self.server_ip.setParent(None)
            self.login_butt.setParent(None)
            self.cancel_butt.setParent(None)
            self.status.setParent(None)

        else:
            self.set_status("Failed\n" + response.get_body())
            # self.cancel_butt.click()
        self.login_butt.setEnabled(False)
        return self.is_loged_in()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.cancel_butt.animateClick()
        elif QKeyEvent.key() == QtCore.Qt.Key_Return\
                or QKeyEvent.key() == QtCore.Qt.Key_Enter:
            self.login_butt.animateClick()
'''
class ClientGui(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.cent_widg = QtGui.QWidget(self)
        self.setCentralWidget(self.cent_widg)
        self.__cl = client.Client()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(200, 200, 800, 600)
        self.show()
        self.pop()


    def pop(self):
        self.login_popup = PopUpLogIn(self.__cl, self)

    def closeEvent(self, QCloseEvent):
        numWindows = len(widgetList)
        if numWindows > 1:
            self.run()
            QCloseEvent.ignore()
        else:
            QCloseEvent.accept()

    def run(self):
        print("hahaha"*10)


'''
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    cl = client.Client()
    chat = PopUpLogIn(cl)
    sys.exit(app.exec_())
