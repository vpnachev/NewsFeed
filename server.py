import socket
import select
import pymongo
from libs.encrypt_hash import encrypt, decrypt
from libs.derser import Message
import time

HOST = '0.0.0.0'
SOCKET_LIST = []
USERNAMES = dict()
RECV_BUFFER = 4096
PORT = 54554
REG_LOG_PORT = 54555


def chat_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    reg_socket = socket.socket()
    reg_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    reg_socket.bind((HOST, REG_LOG_PORT))
    reg_socket.listen(10)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
    SOCKET_LIST.append(reg_socket)
 
    print("Server is available on port:" + str(PORT))
 
    while True:
        import time
        time.sleep(0.01)

        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST,
                                                                [], [], 0)
        time.sleep(0.01)

        for sock in ready_to_read:

            # login
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                buff = sockfd.recv(RECV_BUFFER)
                buff = decrypt(buff)
                if buff != "FAILED" and buff != "":
                    SOCKET_LIST.append(sockfd)
                    uname, password = buff.split('^')
                    print("login " + uname)
                    users = pymongo.MongoClient().chat.users
                    cursor = users.find({"username": uname,
                                         "password": password})
                    if cursor.count() != 1:
                        print('FAILED')
                        sockfd.send(encrypt("FAILED"))
                        sockfd.close()
                        SOCKET_LIST.remove(sockfd)

                    else:
                        print('SUCCESS')
                        USERNAMES[addr] = uname
                        sockfd.send(encrypt("SUCCESS"))
                        print(type(USERNAMES[addr]),
                              type(addr[0]), type(addr[1]))
                        print("Client {}@{}:{} connected".format(
                            USERNAMES[addr], addr[0], addr[1]))
                        data = "{}@{}:{} entered our chatting room\n".format(
                            USERNAMES[addr], addr[0], addr[1])
                        data = encrypt(data)
                        broadcast(server_socket, reg_socket, sockfd, data)
                else:
                    print("Client side failed")

            # register
            elif sock == reg_socket:
                sockfd, addr = reg_socket.accept()
                print("Client ({}, {}) try to reg ...".format(*addr))

                buff = sockfd.recv(RECV_BUFFER)
                buff = decrypt(buff)
                if buff != "FAILED":
                    uname, password = buff.split('^')
                    print("register " + " " + uname)
                    db_client = pymongo.MongoClient()
                    chat = db_client.chat
                    users = chat.users

                    cursor = users.find({"username": uname})
                    if cursor.count() == 0:
                        users.insert({"username": uname, "password": password})
                        print('SUCCESS')
                        sockfd.send(encrypt("SUCCESS"))
                    else:
                        print('FAILED')
                        sockfd.send(encrypt("FAILED"))
                else:
                    print("Client side FAILED")

            # message from client
            else:
                peer = sock.getpeername()
                try:
                    data = sock.recv(RECV_BUFFER)
                    print(data)
                    data = decrypt(data)
                    if data:
                        if data == "LOG OUT":
                            print(USERNAMES[peer], "@", addr[0], ":", addr[1],
                                  " logged out!")
                            data = "Client {}@{}:{} is offline\n".\
                                format(USERNAMES[peer], addr[0], addr[1])
                            data = encrypt(data)
                            broadcast(server_socket, reg_socket, sock, data)
                            if sock in SOCKET_LIST:
                                SOCKET_LIST.remove(sock)
                                del USERNAMES[peer]
                        else:
                            data = "\r" + '[' + USERNAMES[peer] + \
                                   '@{}:{}] '.format(*peer) + data
                            data = encrypt(data)
                            broadcast(server_socket, reg_socket, sock, data)
                    else:
                        print(USERNAMES[peer], "@", addr[0], ":", addr[1],
                              " logged out!")
                        data = "Client {}@{}:{} is offline\n".\
                            format(USERNAMES[peer], addr[0], addr[1])
                        data = encrypt(data)
                        broadcast(server_socket, reg_socket, sock, data)
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)
                            del USERNAMES[peer]

                # exception 
                except BaseException as e:
                    print(e, "exception ", USERNAMES[peer], addr[0], addr[1])
                    broadcast(server_socket, reg_socket, sock, data)
                    continue

    server_socket.close()


# broadcast encrypted chat messages to all connected clients
def broadcast(server_socket, reg_socket, sock, message):
    print("broadcasting message ", message)
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock and socket != reg_socket:
            try:
                socket.send(message)
            except:
                # broken socket connection
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
                    del USERNAMES[socket.getpeername()]
                socket.close()


class Server:
    def __init__(self, listening_addr='127.0.0.1', listening_port=54554,
                 reg_port=54555, db_addr="127.0.0.1", db_port=27017):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((listening_addr, listening_port))
        self._server.listen(128)
        self._server.settimeout(60)
        self._clients = dict()

        self._reg_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._reg_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._reg_server.bind((listening_addr, reg_port))
        self._reg_server.listen(8)
        self._reg_server.settimeout(60)

        self.db_addr = db_addr
        self.db_port = db_port
        self.db_client = None

    def connect_to_db(self):
        if self.db_client:
            self.db_client.close()
        self.db_client = pymongo.MongoClient(self.db_addr, self.db_port)
        time.sleep(2)

    def accept_client(self):
        sock_fd, addr = self._server.accept()
        if not self.log_in(sock_fd, addr):
            sock_fd.close()

    def accept_registration(self):
        reg_sock, addr = self._reg_server.accept()
        self.register(reg_sock)
        reg_sock.close()

    def register(self, sock):
        register_mess = Message("", "")
        register_mess.deserialize(self.receive(sock))

        if register_mess.get_type() != "REGISTER":
            return False
        username = register_mess.get_username()
        password = register_mess.get_password()
        response = Message(username, "REGISTER")

        if not self.db_client.address:
            self.connect_to_db()
        if not self.db_client.address:
            response.set_status("FAILED")
            response.set_body("DB server is not working,"
                              " The registration is not possible!")
            self.send(response, sock)
            return False

        users = self.db_client.chat.users
        cursor = users.find({"username": username})

        if cursor.count() > 0:
            response.set_status("FAILED")
            response.set_body(
                "There is already registered user {}".format(username))
            self.send(response, sock)
            return False

        users.insert({"username": username, "password": password})
        self.send(response, sock)
        return True

    def log_in(self, sock_fd, addr):
        login_mess = Message("", "")
        login_mess.deserialize(self.receive(sock_fd))
        if login_mess.get_type() != "LOGIN":
            return False

        username = login_mess.get_username()
        password = login_mess.get_password()
        response = Message(username, "LOGIN")
        if not self.db_client.address:
            self.connect_to_db()
        if not self.db_client.address:
            print("Mongo DB Server is not working")
            response.set_status("FAILED")
            response.set_body("DB server is not working")
            self.send(response, sock_fd)
            return False

        users = self.db_client.chat.users
        cursor = users.find({"username": username, "password": password})

        if cursor.count() == 0:
            response.set_status("FAILED")
            response.set_body("There is no registered {} user".format(username))
            self.send(response, sock_fd)
            return False

        elif cursor.count() != 1:
            response.set_status("FAILED")
            response.set_body("There is some problems with the server. "
                              "Check the DataBase for more information")
            self.send(response, sock_fd)

        else:
            body = "{}@{}:{} entered our chatting room\n".format(
                username, addr[0], addr[1])
            print(body.format(username, addr[0], addr[1]))
            response.set_body(body)
            self.send(response, sock_fd)
            response.set_type("MESSAGE")
            self.send_to_all_except(response, [])
            self._clients[sock_fd] = (username, addr)
            return True

    def send(self, message, sock_fd):
        transmitted_bytes = 0
        message = message.serialize().encode()
        bytes_to_send = len(message)
        while transmitted_bytes < bytes_to_send:
            transmitted_bytes += sock_fd.send(message[transmitted_bytes:])

    def send_to_all_except(self, message, except_list):
        for dest in self._clients:
            if dest not in except_list:
                self.send(message, dest)

    def handle_message(self, sock):
        message = Message("", "")
        message.deserialize(self.receive(sock))

        message_type = message.get_type()
        if message_type == "MESSAGE":
            self.broadcast_message(sock, message)
        elif message_type == "LOGOUT":
            self.log_out(sock)
        else:
            pass

    def log_out(self, sock):
        notification = Message(self._clients[sock][0], "MESSAGE")
        notification.set_body("User {}@{}:{} have left the room\n".format(
            self._clients[sock][0], self._clients[sock][1][0],
            self._clients[sock][1][1]))
        self.send_to_all_except(notification, [sock])
        del self._clients[sock]

    def broadcast_message(self, sender, message):
        users = self.db_client.chat.messages
        users.insert(message._base_message.copy())
        self.send_to_all_except(message, [sender])

    def receive(self, sock_fd, length=RECV_BUFFER):
        return sock_fd.recv(length).decode()

    def run(self):
        while True:
            ready_socks = self.ready_sockets()
            for sock in ready_socks:
                # login
                if sock == self._server:
                    self.accept_client()
                # register
                elif sock == self._reg_server:
                    self.accept_registration()
                # message
                else:
                    self.handle_message(sock)

    def ready_sockets(self):
        return select.select([x for x in self._clients] +
                             [self._reg_server, self._server], [], [])[0]


def run():
    server = Server()
    server.connect_to_db()
    server.run()


if __name__ == "__main__":
    run()
    # sys.exit(chat_server())
