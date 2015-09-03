import socket
import select
import sys
import pymongo
from libs.derser import Message
import time

HOST = '0.0.0.0'
RECV_BUFFER = 4096
PORT = 54554
REG_LOG_PORT = 54555


class Server:
    def __init__(self, listening_addr=HOST, listening_port=PORT,
                 reg_port=REG_LOG_PORT, db_addr="127.0.0.1", db_port=27017):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((listening_addr, listening_port))
        self._server.listen(128)
        self._server.settimeout(60)
        self._clients = dict()

        print("SERVER is available on host {}:{}".
              format(listening_addr, listening_port))
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

        users.insert({"username": username, "password": password,
                      "likes": 0, "blocks": 0, "blocked_users": []})
        response.set_body("Success")
        response.set_status()
        self.send(response, sock)
        time.sleep(1)
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
            sys.stdout.write(body)
            sys.stdout.flush()
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
        elif message_type == "LIKE":
            owner = message.get_body()
            users = self.db_client.chat.users
            users.update_one({"username": owner}, {"$inc":{"likes": 1}})
        elif message_type == "BLOCK":
            user_to_block = message.get_body()
            user = message.get_username()
            users = self.db_client.chat.users
            users.update_one({"username": user_to_block},
                             {"$inc": {"blocks": 1}})
            users.update_one({"username": user},
                             {"$push":{"blocked_users": user_to_block}})
        elif message_type == "UNBLOCK":
            user = message.get_username()
            user_to_unblock = message.get_body()
            users = self.db_client.chat.users
            users.update_one({"username": user_to_unblock},
                             {"$inc":{"blocks": -1}})
            users.update_one({"username": user},
                             {"$pull": {"blocked_users": user_to_unblock}})
        else:
            pass

    def log_out(self, sock):
        notification = Message(self._clients[sock][0], "MESSAGE")
        notification.set_body("User {}@{}:{} have left the room\n".format(
            self._clients[sock][0], self._clients[sock][1][0],
            self._clients[sock][1][1]))
        self.send_to_all_except(notification, [sock])
        del self._clients[sock]
        sys.stdout.write(notification.get_body())
        sys.stdout.flush()

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


def run(host, port, reg_port):
    server = Server(host, port, reg_port)
    server.connect_to_db()
    server.run()


if __name__ == "__main__":
    host = HOST
    port = PORT
    reg_port = REG_LOG_PORT
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        reg_port = int(sys.argv[3])

    run(host, port, reg_port)
    # sys.exit(chat_server())
