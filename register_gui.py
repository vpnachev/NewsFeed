from PyQt4 import QtCore, QtGui
import sys
import register
from libs.encrypt_hash import crypto


class RegisterGui(QtGui.QWidget):
    def __init__(self):
        self.__registrator = register.Register()
        QtGui.QWidget.__init__(self)
        self.init_gui()

    def set_server_address(self, host, port):
        self.__registrator.set_server(host, port)

    def set_response_text(self, text):
        self.__response_text.setText(text)

    def register(self):
        self.set_response_text("")
        if len(self.__server_addr.text()) == 0:
            self.set_response_text("Empty server address")
            return False

        if int(self.__server_port.text()) not in range(1, 2**16 + 1):
            self.set_response_text("Empty or incorrect port")
            return False

        if len(self.__user_text.text()) == 0:
            self.set_response_text("Empty username")
            return False

        if len(self.__pass_text.text()) == 0:
            self.set_response_text("Empty password field")
            return False

        if len(self.__pass_confirm.text()) == 0:
            self.set_response_text("Empty password confirmation field")
            return False

        self.set_server_address(self.__server_addr.text(),
                                int(self.__server_port.text()))
        uname = self.__user_text.text()
        passwd = self.__pass_text.text()
        confirm = self.__pass_confirm.text()
        if passwd != confirm:
            self.set_response_text("Password and Confirm Passwrod mismatch\n")
            return False

        passwd = crypto(passwd)
        status, response = self.__registrator.register(uname, passwd)
        self.set_response_text(response.get_status() + "\n" +
                               response.get_body())
        if not status:
            self.set_response_text(self.__response_text.text() +
                                   "\nRestart the application "
                                   "if you want to retry")
        self.__register_button.setEnabled(False)

    def init_gui(self):
        self.__register_button = QtGui.QPushButton("&Register", self)

        self.__server_addr = QtGui.QLineEdit("127.0.0.1")
        self.__server_port = QtGui.QLineEdit("54555")

        self.__user_text = QtGui.QLineEdit()
        self.__user_text.setPlaceholderText("USERNAME")

        self.__pass_text = QtGui.QLineEdit()
        self.__pass_text.setPlaceholderText("Password")
        self.__pass_text.setEchoMode(2)

        self.__pass_confirm = QtGui.QLineEdit()
        self.__pass_confirm.setPlaceholderText("Confirm Password")
        self.__pass_confirm.setEchoMode(2)

        grid_layout = QtGui.QGridLayout()

        grid_layout.addWidget(self.__server_addr, 0, 0)
        grid_layout.addWidget(self.__server_port, 0, 1)
        grid_layout.addWidget(self.__user_text, 1, 0)
        grid_layout.addWidget(self.__pass_text, 1, 1)
        grid_layout.addWidget(self.__pass_confirm, 2, 1)
        grid_layout.addWidget(self.__register_button, 3, 0, 1, 2)
        # grid_layout.setColumnStretch(1,1)
        # grid_layout.setColumnStretch(0,1)

        self.__response_text = QtGui.QLabel()
        grid_layout.addWidget(self.__response_text, 4, 0, 10, 2)
        self.__response_text.setText(("\n"*5))
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setRowStretch(2, 1)
        grid_layout.setRowStretch(3, 1)

        self.__register_button.clicked.connect(self.register)
        self.setLayout(grid_layout)
        self.setGeometry(150, 150, 350, 100)
        self.setWindowTitle("User Registration.")
        self.show()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif QKeyEvent.key() == QtCore.Qt.Key_Enter \
                or QKeyEvent.key() == QtCore.Qt.Key_Return:
            self.__register_button.animateClick()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    inst = RegisterGui()
    sys.exit(app.exec_())
