# chat_client.py

import sys
import socket
import select
import getpass
import derser
from  libs.encrypt_hash import crypto, encrypt, decrypt


RECV_BUFFER = 4096
USER = ""


def login(log_s):
    global USER
    sys.stdout.write("<username>: ")
    sys.stdout.flush()
    uname = sys.stdin.readline()
    uname = uname.split("\n")[0]

    password = getpass.getpass("<password>:")
    password = crypto(password)

    log_s.send(encrypt(uname+'^'+password))

    ans = log_s.recv(RECV_BUFFER)
    ans = decrypt(ans)
    if ans == "SUCCESS":
        USER = uname
        return True
    else:
        return False


def chat_client():
    global USER
    if len(sys.argv) < 0:
        print('Usage : python client.py')
        sys.exit()

    if len(sys.argv) >= 2:
        host = sys.argv[1]
    else:
        host = "127.0.0.1"
    port = 54554
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(100)

    try:
        s.connect((host, port))
    except:
        print('Unable to connect')
        sys.exit()

    if not login(s):
        print("Login failed")
        sys.exit()

    print('Connected to remote host. You can start sending messages')
    sys.stdout.write('[{}]: '.format(USER))
    sys.stdout.flush()

    socket_list = [sys.stdin, s]

    import time
    try:
        while True:

            time.sleep(0.01)
            ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])
            time.sleep(0.01)

            for sock in ready_to_read:
                if sock == s:
                    data = sock.recv(RECV_BUFFER)
                    data = decrypt(data)
                    if not data:
                        print('\nDisconnected from chat server')
                        sys.exit()
                    else:
                        # print data
                        sys.stdout.write(data)
                        sys.stdout.write('[{}]: '.format(USER))
                        sys.stdout.flush()

                else:
                    # user entered a message
                    msg = sys.stdin.readline()
                    msg = encrypt(msg)
                    s.send(msg)
                    sys.stdout.write('[{}]: '.format(USER))
                    sys.stdout.flush()
    except KeyboardInterrupt:
        msg = "LOG OUT"
        s.send(encrypt(msg))
        s.close()
        print("Good bye")
        sys.exit()


class Client:
    def __init__(self, server_addr, server_port):
        self._server = (server_addr, server_port)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(60)

    def connect(self):
        self._server_socket.connect(self._server)

    def send(self, message):
        transmitted_bytes = self._server_socket.send(message)
        bytes_to_send = len(message)
        while transmitted_bytes < bytes_to_send:
            transmitted_bytes += self._server_socket.send(message[transmitted_bytes:])

    def receive(self, length):
        return self._server_socket.recv(length)

    def log_in(self):
        pass

    def run(self):
        pass


if __name__ == "__main__":
    sys.exit(chat_client())
