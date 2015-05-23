''' This is simple wrapper library for encryption and decryption of strings
    It also provides hashing method for passwords(sha256)
'''

from hashlib import sha256
from simplecrypt import encrypt as encr, decrypt as decr

CYPHER = "PASSWORD"


def crypto(x):
    return sha256(x.encode()).hexdigest()


def encrypt(data, cypher=CYPHER):
    #return data.encode()
    return encr(cypher, data)


def decrypt(data, cypher=CYPHER):
    #return data.decode('utf-8')
    return decr(cypher, data).decode('utf-8')