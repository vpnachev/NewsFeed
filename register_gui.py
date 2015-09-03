from PyQt4 import QtCore, QtGui
import sys
import register
from libs.encrypt_hash import crypto
from libs.derser import Message

class RegisterGui(register.Register, QtGui.QWidget):
    def __init__(self):
        register.Register.__init__(self)
        QtGui.QMainWindow.__init__(self)
        # super(RegisterGui, self).__init__()
        self.init_gui()

    def set_server_address(self, host, port):
        register.Register.set_server(self, host, port)

    # def connect(self):
    #    return register.Register.connect(self)

    def set_responce_text(self, text):
        self.__response_text.setText(text)

    def register(self):
        self.set_responce_text("")
        if len(self.__server_addr.text()) == 0:
            self.set_responce_text("Empty server address")
            return False

        if len(self.__server_port.text()) == 0 or \
                not(0 < int(self.__server_port.text()) and
                int(self.__server_port.text()) < 65534):
            self.set_responce_text("Empty or incorrect port")
            return False

        if len(self.__user_text.text()) == 0:
            self.set_responce_text("Empty username")
            return False

        if len(self.__pass_text.text()) == 0:
            self.set_responce_text("Empty password field")
            return False

        self.set_server_address(self.__server_addr.text(),
                        int(self.__server_port.text()))
        uname = self.__user_text.text()
        passwd = self.__pass_text.text()
        print(uname, passwd, crypto(passwd), sep="  ")
        passwd = crypto(passwd)
        print(passwd)
        status, response = register.Register.register(
                self,
                uname,
                passwd)
        self.set_responce_text(response.get_status() + "\n"+
                               response.get_body())

    def init_gui(self):
        self.__register_button = QtGui.QPushButton("Register", self)
        grid_layout = QtGui.QGridLayout()
        grid_layout.addWidget(self.__register_button, 2, 0, 1, 2)

        self.__server_addr = QtGui.QLineEdit("127.0.0.1")
        self.__server_port = QtGui.QLineEdit("54555")
        self.__user_text = QtGui.QLineEdit()
        self.__user_text.setPlaceholderText("USERNAME")
        self.__pass_text = QtGui.QLineEdit()
        self.__pass_text.setPlaceholderText("Password")
        self.__pass_text.setEchoMode(2)

        grid_layout.addWidget(self.__server_addr, 0, 0)
        grid_layout.addWidget(self.__server_port, 0, 1)
        grid_layout.addWidget(self.__user_text, 1, 0)
        grid_layout.addWidget(self.__pass_text, 1, 1)
        # grid_layout.setColumnStretch(1,1)
        # grid_layout.setColumnStretch(0,1)

        self.__response_text = QtGui.QLabel()
        grid_layout.addWidget(self.__response_text, 3, 0, 10, 2)
        self.__response_text.setText(("\n"*5))
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setRowStretch(2, 1)

        self.__register_button.clicked.connect(self.register)
        self.setLayout(grid_layout)
        self.setGeometry(150, 150, 350, 100)
        self.setWindowTitle("User Registration.")
        self.show()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    inst = RegisterGui()
    sys.exit(app.exec_())
