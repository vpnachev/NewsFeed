# this module provide basic functions for communication between two nodes
MAGIC = 128
MORE_MAGIC = 42
import socket


class Connector():
    def __init__(self, host="127.0.0.1", port=54554):
        self.host = host
        self.port = port
        self.listening_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
        self.listening_socket.bind((self.host, self.port))
        self.listening_socket.listen(MAGIC)

    def connect(self, remote_destination):
        """remote destination is represented by the pair(IP<str>, port<int>)"""
        try:
            self.listening_socket.connect(remote_destination)
        except Exception as e:
            print(e.message)
            raise

    def send_message(self, message, encrypted=False):
        pass

    def disconnect(self):
        pass