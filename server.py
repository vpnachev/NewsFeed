import sys
import socket
import select
import pymongo

HOST = '' 
SOCKET_LIST = set()
RECV_BUFFER = 4096 
PORT = 54554
REG_PORT = 54555

def chat_server():

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    reg_socket = socket.socket()
    reg_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    reg_socket.bind((HOST, REG_PORT))
    reg_socket.listen(10)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.add(server_socket, reg_socket)
 
    print("Chat server started on port " + str(PORT))
 
    while True:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)

        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.add(sockfd)
                print("Client ({}, {}) connected".fromat(addr))
                 
                broadcast(server_socket, sockfd, "[{}:{}] entered our chatting room\n".format(addr))
            
            else if sock == reg_socket:
                sockfd, addr = reg_socket.accept()
                print("Client ({}, {}) start registration...".fromat(addr))
                uname = sockfd.recv(RECV_BUFFER)
                password = sock.recv(RECV_BUFFER)
                password = hash(password)
                db_client = pymongo.MongoClient()
                chat = db_client.chat
                users = chat.users

                curs = users.find({"username" : uname})
                if curs.count == 0:
                    users.insert("username" : uname, "password" : password)
                    sockfd.send("SUCCESSFUL REGISTRATION :)")
                else:
                    sockfd.send("REGISTRATION FAILED, INVALID CREDENTIALS :(")

            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "Client ({}, {}) is offline\n".format(addr)) 

                # exception 
                except:
                    broadcast(server_socket, sock, "Client ({}, {}) is offline\n".format(addr))
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
 
if __name__ == "__main__":

    sys.exit(chat_server())