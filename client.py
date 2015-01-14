# chat_client.py

import sys
import socket
import select
import getpass
from hashlib import sha256


def crypto(x):
    return str(sha256(x).hexdigest())


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

    log_s.send(uname+'^'+password)

    ans = log_s.recv(RECV_BUFFER)
    if ans == "SUCCESS":
        USER = uname
        return True
    elif ans == "FAILED":
        return False
    else:
        return False

def chat_client():
    global USER
    if(len(sys.argv) < 0):
        print 'Usage : python client.py'
        sys.exit()

    host = "127.0.0.1"
    port = 54554
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)

    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()

    if login(s) == False:
        print "Login failed"
        sys.exit()

    print 'Connected to remote host. You can start sending messages'
    sys.stdout.write('[{}]: '.format(USER))
    sys.stdout.flush()
     
    while True:
        socket_list = [sys.stdin, s]
        ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
         
        for sock in ready_to_read:             
            if sock == s:
                data = sock.recv(RECV_BUFFER)
                if not data :
                    print '\nDisconnected from chat server'
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data)
                    sys.stdout.write('[{}]: '.format(USER))
                    sys.stdout.flush()
            
            else :
                # user entered a message
                msg = sys.stdin.readline()
                s.send(msg)
                sys.stdout.write('[{}]: '.format(USER))
                sys.stdout.flush()

if __name__ == "__main__":
    sys.exit(chat_client())