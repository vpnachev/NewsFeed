# chat_client.py

import sys
import socket
import select
import getpass
from libs.derser import Message
from libs.encrypt_hash import crypto


RECV_BUFFER = 4096


class Client:
    """
    This object represents one client it the chat room.
    It is created with the address and port of the server, as the address
    is passed as string, while the port as number.
    The default server is working on 127.0.0.1:54554
    Also, you can specify only the address and use the default port
    Example:
    cl = Client("10.11.12.13", 12345)
    Here the cl will expect working server on 10.11.12.13:12345

    cl_def_port = Client("100.101.102.103")
    Here the cl_def_port will expect working server on 100.101.102.103:54554
    """
    def __init__(self, server_addr="127.0.0.1", server_port=54554):
        self._server = (server_addr, server_port)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(60)
        self.username = None

    def connect(self):
        try:
            self._server_socket.connect(self._server)
        except OSError as err:
            print(err)
            return False
        return True

    def __send(self, message):
        message = message.encode()
        transmitted_bytes = 0
        bytes_to_send = len(message)
        while transmitted_bytes < bytes_to_send:
            transmitted_bytes += \
                self._server_socket.send(message[transmitted_bytes:])

    def receive(self, length=RECV_BUFFER):
        return self._server_socket.recv(length).decode()

    def log_in(self, username, password):
        log_in_message = Message(username, "LOGIN")
        log_in_message.set_password(password)

        self.__send(log_in_message.serialize())
        response = Message(username, "LOGIN")
        response.deserialize(self.receive())
        if response.get_status() == "OK":
            self.username = username
            return True
        print(response.get_body())
        return False

    def log_out(self):
        log_out_message = Message(self.username, "LOGOUT")
        self.__send(log_out_message.serialize())
        self._server_socket.close()

    def like(self, message_timestamp, owner):
        pass

    def block_user(self, user_to_block):
        block_message = Message(self.username, "BLOCK")
        block_message.set_body(user_to_block)
        self.__send(block_message.serialize())

    def unblock_user(self, user_to_unblock):
        unblock_message = Message(self.username, "UNBLOCK")
        unblock_message.set_body(user_to_unblock)
        self.__send(unblock_message.serialize())

    def load20_more_messages(self, oldest_message):
        pass

    def send_message(self, body):
        mess = Message(self.username, "MESSAGE")
        mess.set_body(body)
        self.__send(mess.serialize())

    def handle_message(self, message):
        if message.get_type() == "MESSAGE":
            text = "\n[{}]:{} ".format(message.get_username(),
                                       message.get_body())
            sys.stdout.write(text)
            sys.stdout.write("[{}]:".format(self.username))
            sys.stdout.flush()

        else:
            pass

    def run(self):
        if not self.connect():
            return

        sys.stdout.write("<username>: ")
        sys.stdout.flush()
        self.username = sys.stdin.readline().split("\n")[0]
        password = getpass.getpass("<password>:")
        password = crypto(password)
        if not self.log_in(self.username, password):
            return

        del password
        sys.stdout.write('[{}]: '.format(self.username))
        sys.stdout.flush()
        while True:
            ready_socks = select.select(
                [sys.stdin, self._server_socket], [], [])[0]
            for sock in ready_socks:
                if sock == sys.stdin:
                    body = sys.stdin.readline()
                    self.send_message(body)
                    sys.stdout.write('[{}]: '.format(self.username))
                    sys.stdout.flush()
                else:
                    recv_message = Message("", "")
                    x = self.receive()
                    # print(x)
                    recv_message.deserialize(x)
                    self.handle_message(recv_message)


def run():
    client = Client()
    try:
        client.run()
    except KeyboardInterrupt:
        client.log_out()
        return


if __name__ == "__main__":
    # s ys.exit(chat_client())
    run()
