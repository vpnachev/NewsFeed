# registration panel

import sys
import socket
import getpass
from libs.encrypt_hash import crypto
from libs.derser import Message

RECV_BUFFER = 4096


class Register:
    def __init__(self, server_addr="127.0.0.1", server_port=54555):
        self._server = (server_addr, server_port)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(60)

    def __del__(self):
        self._server_socket.close()

    def register(self, username, password):
        '''
        :param username: username as string
        :param password: sha256 hash of password
        :return: True on successful registration, False otherwise
        '''
        reg_message = Message(username, "REGISTER")
        reg_message.set_password(password)
        response_msg = Message(username, "REGISTER")
        if self.connect() == False:
            print("Connection problems")
            response_msg.set_body("Connection problems")
            response_msg.set_status("FAILED")
            return False, response_msg

        self.send(reg_message)
        response_msg = self.receive()
        if response_msg.get_type() != "REGISTER":
            print("Non REGISTER message was sent from server")
            return False, response_msg
        if response_msg.get_status() == "OK":
            print("Successful Registration")
            return (True, response_msg)
        elif response_msg.get_status() == "FAILED":
            print(response_msg.get_body())
            return False, response_msg

    def receive(self, length=RECV_BUFFER):
        m = Message("", "")
        m.deserialize(self._server_socket.recv(length).decode())
        return m

    def send(self, message):
        transmitted_bytes = 0
        message = message.serialize().encode()
        bytes_to_send = len(message)
        while transmitted_bytes < bytes_to_send:
            transmitted_bytes += \
                self._server_socket.send(message[transmitted_bytes:])

    def connect(self):
        try:
            self._server_socket.connect(self._server)
        except OSError as err:
            print(err)
            return False
        return True

    def close(self):
        self._server_socket.close()

    def set_server(self, host, port):
        """
        :param host: Hostname or IP of server as string
        :param port: Listening port of server as integer
        """
        self._server = (host, port)


if __name__ == "__main__":
    # sys.exit(register())
    client = Register()
    # get new username
    sys.stdout.write('<username>: ')
    sys.stdout.flush()
    uname = sys.stdin.readline()
    uname = uname.split('\n')[0]

    # get password
    init_pass = getpass.getpass("<password>:")
    confirm_pass = getpass.getpass("<confirm password>:")
    if init_pass != confirm_pass:
        sys.stdout.write("wrong password!")
        sys.stdout.flush()
        sys.exit(2)

    init_pass = crypto(init_pass)
    if client.register(uname, init_pass):
        print("Success")
    else:
        print("Failed")
