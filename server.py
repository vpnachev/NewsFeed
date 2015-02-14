import time
import sys
import socket
import select
import pymongo
from simplecrypt import encrypt as encr, decrypt as decr

HOST = '0.0.0.0'
SOCKET_LIST = []
USERNAMES = dict()
RECV_BUFFER = 4096
PORT = 54554
REG_LOG_PORT = 54555
CYPHER = "PASSWORD"


def encrypt(CYPHER, data):
    return data.encode()
    # return encr(CYPHER, data)


def decrypt(CYPHER, data):
    return data.decode('utf-8')
    # return decr(CYPHER, data).decode('utf-8')


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
        time.sleep(0.01)

        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST, [], [], 0)
        time.sleep(0.01)

        for sock in ready_to_read:

            # login
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                buff = sockfd.recv(RECV_BUFFER)
                buff = decrypt(CYPHER, buff)
                if buff != "FAILED" and buff !="":
                    SOCKET_LIST.append(sockfd)
                    uname, password = buff.split('^')
                    print("login " + uname)
                    users = pymongo.MongoClient().chat.users
                    cursor = users.find({"username": uname, "password": password})
                    if cursor.count() != 1:
                        print('FAILED')
                        sockfd.send(encrypt(CYPHER,"FAILED"))
                        sockfd.close()
                        SOCKET_LIST.remove(sockfd)

                    else:
                        print('SUCCESS')
                        USERNAMES[addr] = uname
                        sockfd.send(encrypt(CYPHER,"SUCCESS"))
                        print(type(USERNAMES[addr]), type(addr[0]), type(addr[1]))
                        print("Client {}@{}:{} connected".format(USERNAMES[addr], addr[0], addr[1]))
                        data = "{}@{}:{} entered our chatting room\n".format(USERNAMES[addr], addr[0], addr[1])
                        data = encrypt(CYPHER, data)
                        broadcast(server_socket, reg_socket, sockfd, data)
                else:
                    print("Client side failed")

            # register
            elif sock == reg_socket:
                sockfd, addr = reg_socket.accept()
                print("Client ({}, {}) try to reg ...".format(*addr))

                buff = sockfd.recv(RECV_BUFFER)
                buff = decrypt(CYPHER, buff)
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
                        sockfd.send(encrypt(CYPHER, "SUCCESS"))
                    else:
                        print('FAILED')
                        sockfd.send(encrypt(CYPHER, "FAILED"))
                else:
                    print("Client side FAILED")

            # message from client
            else:
                peer = sock.getpeername()
                try:
                    data = sock.recv(RECV_BUFFER)
                    print(data)
                    data = decrypt(CYPHER, data)
                    if data:
                        if data == "LOG OUT":
                            print(USERNAMES[peer],"@", addr[0],":", addr[1], " logged out!")
                            data = "Client {}@{}:{} is offline\n".format(USERNAMES[peer], addr[0], addr[1])
                            data = encrypt(CYPHER, data)
                            broadcast(server_socket, reg_socket, sock, data)
                            if sock in SOCKET_LIST:
                                SOCKET_LIST.remove(sock)
                                del USERNAMES[peer]
                        else:
                            data = "\r" + '[' + USERNAMES[peer] + '@{}:{}] '.format(*peer) + data
                            data = encrypt(CYPHER, data)
                            broadcast(server_socket, reg_socket, sock, data)
                    else:
                        print(USERNAMES[peer],"@", addr[0],":", addr[1], " logged out!")
                        data = "Client {}@{}:{} is offline\n".format(USERNAMES[peer], addr[0], addr[1])
                        data = encrypt(CYPHER, data)
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
 
if __name__ == "__main__":
    sys.exit(chat_server())
