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
        grid_layout = QtGui.QGridLayout()
        grid_layout.addWidget(register_button, 2, 0, 1, 2)

        server_addr = QtGui.QLineEdit("127.0.0.1")
        server_port = QtGui.QLineEdit("54555")
        user_text = QtGui.QLineEdit()
        user_text.setPlaceholderText("USERNAME")
        pass_text = QtGui.QLineEdit()
        pass_text.setPlaceholderText("Password")
        pass_text.setEchoMode(2)

        grid_layout.addWidget(server_addr, 0, 0)
        grid_layout.addWidget(server_port, 0, 1)
        grid_layout.addWidget(user_text, 1, 0)
        grid_layout.addWidget(pass_text, 1, 1)
        # grid_layout.setColumnStretch(1,1)
        # grid_layout.setColumnStretch(0,1)

        response_text = QtGui.QLabel()
        grid_layout.addWidget(response_text,3, 0, 10, 2)
        response_text.setText(("\n"*5))
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setRowStretch(2, 1)

        self.setLayout(grid_layout)
        self.setGeometry(150, 150, 350, 100)
        self.setWindowTitle("User Registration.")
        self.show()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    inst = RegisterGui()
    sys.exit(app.exec_())