#registration panel

import sys
import socket
import getpass
from hashlib import sha256
from simplecrypt import encrypt as encr, decrypt as decr

def crypto(x):
    return str(sha256(x).hexdigest())

CYPHER = "PASSWORD"

def encrypt(CYPHER, data):
    return data.encode()
    # return encr(CYPHER, data)

def decrypt(CYPHER, data):
    return data.decode()
    # return decr(CYPHER, data).decode()

RECV_BUFFER = 4096


def register():
    if len(sys.argv) > 1:
        print('Usage : python register.py')
        sys.exit()

    host = "127.0.0.1"
    port = 54555
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)

    try:
        s.connect((host, port))
    except:
        print('Unable to connect')
        sys.exit()

    print('Connected to server. You can start registration procedure')
    sys.stdout.write('<username>: ')
    sys.stdout.flush()
    uname = sys.stdin.readline()
    uname = uname.split('\n')[0]

    print("Don`t use '^' character in your password")
    init_pass = getpass.getpass("<password>:")
    confirm_pass = getpass.getpass("<confirm password>:")
    if init_pass != confirm_pass:
        print("wrong password!")
        s.send(encrypt(CYPHER, "FAILED"))
        sys.exit()
    if "^" in init_pass:
        print("Not allowed characters in your password")
        s.send(encrypt(CYPHER, "FAILED"))
        sys.exit()

    password = crypto(confirm_pass)
    s.send(encrypt(CYPHER, uname + "^" + password))

    ans = s.recv(RECV_BUFFER)
    ans = decrypt(CYPHER, ans)
    s.close()
    if ans == "SUCCESS":
        print("Successful registration of user {}".format(uname))
    elif ans == "FAILED":
        print("FAILD!!! username {} is already used".format(uname))

if __name__ == "__main__":
    sys.exit(register())