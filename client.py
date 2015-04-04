# chat_client.py

import time, derser, sys, socket, select, getpass
import hashlib
from simplecrypt import encrypt as encr, decrypt as decr

def crypto(x):
    return hashlib.sha256(x.encode()).hexdigest()


RECV_BUFFER = 4096
USER = ""
CYPHER = "PASSWORD"

def encrypt(CYPHER, data):
    return data.encode()
    # return encr(CYPHER, data)

def decrypt(CYPHER, data):
    return data.decode()
    #  return decr(CYPHER, data).decode()

def login(log_s):
    global USER
    sys.stdout.write("<username>: ")
    sys.stdout.flush()
    uname = sys.stdin.readline()
    uname = uname.split("\n")[0]

    password = getpass.getpass("<password>:")
    password = crypto(password)

    log_s.send(encrypt(CYPHER, (uname+'^'+password)))

    ans = log_s.recv(RECV_BUFFER)
    ans = decrypt(CYPHER, ans)
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

    try:
        while True:

            time.sleep(0.01)
            ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])
            time.sleep(0.01)

            for sock in ready_to_read:
                # recieve message from server
                if sock == s:
                    data = sock.recv(RECV_BUFFER)
                    data = decrypt(CYPHER, data)
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
                    msg = encrypt(CYPHER, msg)
                    s.send(msg)
                    sys.stdout.write('[{}]: '.format(USER))
                    sys.stdout.flush()
    except KeyboardInterrupt:
        msg = "LOG OUT"
        s.send(encrypt(CYPHER, msg))
        s.close()
        print("Good bye")
        sys.exit()


if __name__ == "__main__":
    sys.exit(chat_client())