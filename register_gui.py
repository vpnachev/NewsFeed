from PyQt4 import QtCore, QtGui
import sys
import register

class RegisterGui(QtGui.QWidget, register.Register):
    def __init__(self):
        # register.Register.__init__(self)
        # QtGui.QMainWindow.__init__(self)
        super(RegisterGui, self).__init__()
        self.init_gui()

    def set_server_address(self, host, port):
        self.set_server(host, port)

    def connect(self):
        return register.Register.connect(self)

    def register(self):
        pass

    def init_gui(self):
        register_button = QtGui.QPushButton("Register", self)
        connect_button = QtGui.QPushButton("Connect to server", self)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(register_button)
        vbox.addWidget(connect_button)
        vbox.addStretch(1)
        hbox = QtGui.QHBoxLayout()

        server_addr = QtGui.QLineEdit("127.0.0.1")
        server_port = QtGui.QLineEdit("54555")
        user_text = QtGui.QLineEdit()
        user_text.setPlaceholderText("USERNAME")
        pass_text = QtGui.QLineEdit()
        pass_text.setPlaceholderText("Password")
        pass_text.setEchoMode(2)

        vbox_cred_layout = QtGui.QVBoxLayout()
        vbox_cred_layout.addWidget(server_addr)
        vbox_cred_layout.addWidget(server_port)
        vbox_cred_layout.addWidget(user_text)
        vbox_cred_layout.addWidget(pass_text)
        vbox_cred_layout.addStretch(1)

        hbox.addLayout(vbox_cred_layout)
        hbox.addLayout(vbox)
        self.setLayout(hbox)

        self.setGeometry(150, 150, 350, 100)
        self.setWindowTitle("User Registration.")
        self.show()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    inst = RegisterGui()
    sys.exit(app.exec_())