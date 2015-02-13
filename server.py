import sys
import socket
import select
import pymongo
from simplecrypt import encrypt,decrypt

HOST = '0.0.0.0'
SOCKET_LIST = []
USERNAMES = dict()
RECV_BUFFER = 4096
PORT = 54554
REG_LOG_PORT = 54555
CIPHER = "PASSWORD"

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
 
    print"Server is available on port:" + str(PORT)
 
    while True:

        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST, [], [], 0)

        for sock in ready_to_read:

            # login
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                buff = sockfd.recv(RECV_BUFFER)
                if buff != "FAILED":
                    uname, password = buff.split('^')
                    print "login " + uname
                    users = pymongo.MongoClient().chat.users
                    cursor = users.find({"username":uname, "password":password})
                    if cursor.count() != 1:
                        print 'FAILED'
                        sockfd.send("FAILED")
                        sockfd.close()
                        SOCKET_LIST.remove(sockfd)

                    else:
                        print 'SUCCESS'
                        USERNAMES[addr] = uname
                        sockfd.send("SUCCESS")
                        print "Client {}@{}:{} connected".format(USERNAMES[addr],addr[0], addr[1])
                        data = "{}@{}:{} entered our chatting room\n".format(USERNAMES[addr], addr[0], addr[1])
                        data = encrypt(CIPHER, data)
                        broadcast(server_socket, reg_socket, sockfd, data)
                else:
                    print "Client side failed"

            #register
            elif sock == reg_socket:
                sockfd, addr = reg_socket.accept()
                print "Client ({}, {}) try to reg ...".format(*addr)

                buff = sockfd.recv(RECV_BUFFER)
                if buff != "FAILED":
                    uname, password = buff.split('^')
                    print "register " + " " + uname
                    db_client = pymongo.MongoClient()
                    chat = db_client.chat
                    users = chat.users

                    cursor = users.find({"username":uname})
                    if cursor.count() == 0:
                        users.insert({"username":uname, "password":password})
                        print 'SUCCESS'
                        sockfd.send("SUCCESS")
                    else:
                        print 'FAILED'
                        sockfd.send("FAILED")
                else:
                    print "Client side FAILED"

            # message from client
            else:
                peer = sock.getpeername()
                try:
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        data = decrypt(CIPHER,data)
                        data = "\r" + '[' + USERNAMES[peer]+ '@{}:{}] '.format(*peer) + data
                        data = encrypt(CIPHER, data)
                        broadcast(server_socket, reg_socket, sock, data)
                    else:
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)
                            del USERNAMES[peer]

                        data = "Client {}@{}:{} is offline\n".format(USERNAMES[peer],addr[0], addr[1])
                        data = encrypt(CIPHER, data)
                        broadcast(server_socket, reg_socket, sock, data)

                # exception 
                except:
                    data = "Client {}@{}:{} is offline\n".format(USERNAMES[peer],addr[0], addr[1])
                    data = encrypt(CIPHER, data)
                    broadcast(server_socket, reg_socket, sock, data)
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, reg_socket, sock, message):
    print message
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock  and socket != reg_socket:
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
                    del USERNAMES[socket.getpeername()]
 
if __name__ == "__main__":
    sys.exit(chat_server())
