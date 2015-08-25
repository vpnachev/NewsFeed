# registration panel

import sys
import socket
import getpass
from libs.encrypt_hash import encrypt, decrypt, crypto, CYPHER
from libs.derser import Message

RECV_BUFFER = 4096


class Register:
    def __init__(self, server_addr="127.0.0.1", server_port=54555):
        self._server = (server_addr, server_port)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(60)

    def register(self):
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
            return False

        reg_message = Message(uname, "REGISTER")
        reg_message.set_password = crypto(confirm_pass)
        reg_message.set_status()

        if self.connect() is False:
            print("Connection problems")
            return False

        self.send(reg_message.serialize())
        response_msg = Message(uname, "REGISTER")
        response_msg.deserialize(self.receive(RECV_BUFFER))
        self.close()
        if response_msg.get_status() == "OK":
            print("Successful Registration")
            return True
        elif response_msg.get_status() == "FAILED":
            print(response_msg.get_body())
            return False
        else:
            pass

    def receive(self, length):
        return self._server_socket.recv(length)

    def send(self, message):
        transmitted_bytes = self._server_socket.send(message)
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


def register():
    if len(sys.argv) > 1:
        print('Usage : python register.py')
        sys.exit()

    host = "127.0.0.1"
    port = 54555
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)

    try:
        s.connect((host, port))
    except OSError:
        print('Unable to connect')
        sys.exit()
    print('Connected to server. You can start registration procedure')

    sys.stdout.write('<username>: ')
    sys.stdout.flush()
    uname = sys.stdin.readline()
    uname = uname.split('\n')[0]

    print("Don`t use '^' character in your password")
    init_pass = getpass.getpass("<password>:")
    confirm_pass = getpass.getpass("<confirm password>:")
    if init_pass != confirm_pass:
        print("wrong password!")
        s.send(encrypt(CYPHER, "FAILED"))
        sys.exit()
    if "^" in init_pass:
        print("Not allowed characters in your password")
        s.send(encrypt(CYPHER, "FAILED"))
        sys.exit()

    password = crypto(confirm_pass)
    s.send(encrypt(CYPHER, uname + "^" + password))

    ans = s.recv(RECV_BUFFER)
    ans = decrypt(CYPHER, ans)
    s.close()
    if ans == "SUCCESS":
        print("Successful registration of user {}".format(uname))
    elif ans == "FAILED":
        print("FAILD!!! username {} is already used".format(uname))

if __name__ == "__main__":
    # sys.exit(register())
    client = Register()
    if client.register():
        print("SuccessSSSSSSSSSSSSSSSSSSS")
    else:
        print("adjnasjdknasodijnasmd asoidj aps")

