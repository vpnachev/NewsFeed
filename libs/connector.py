# this module provide basic functions for communication between two nodes


class Connector():
    def __init__(self, addr, port):
        self._addr = addr
        self._port = port

    def connect(self, ip, port):
        pass

    def send(self, message, encrypted=False):
        pass

    def receive(self, length, encrypted=False):
        pass

    def disconnect(self):
        pass
