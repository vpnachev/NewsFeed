"""
This is simple serialize/deserialize lib/

It convert builtin.dict to stringed json -> serialize
and vice versa
stringed json do dict -> deserialize
"""
from json import dumps, loads
import time


def serialize(dict_arg):
    return dumps(dict_arg, ensure_ascii=False)


def deserialize(str_arg):
    return loads(str_arg)


class Message:
    """
    MESSAGE INTERFACE
    {
        "TYPE": ["REGISTER", "LOGIN", "LOGOUT", "MESSAGE", "LIKE",
                "BLOCK", "UNBLOCK", "20_MORE", "AVATAR"]
        "DATETIME": ["15:43:55/14.02.2015] -> utc time/gmt+00
        "STATUS": ["OK", "FAILED"],
        "USERNAME": "login/register username",
        "PASSWORD": "password, used only for authentication and registration",
        "BODY": "TEXT"
    }
    """
    def __init__(self, username, type_of_message):
        self._base_message = dict(TYPE=type_of_message, USERNAME=username)
        self.set_datetime()
        self.set_status()

    def set_password(self, password):
        """ here password is already hashed with sha256"""
        self._base_message['PASSWORD'] = password

    def set_body(self, body):
        """ Here body is the text of message or content of transmitted file"""
        self._base_message['BODY'] = body

    def set_status(self, status='OK'):
        self._base_message['STATUS'] = status

    def set_datetime(self):
        self._base_message["DATETIME"] = time.asctime(time.gmtime())

    def set_username(self, username):
        self._base_message["USERNAME"] = username

    def set_type(self, message_type):
        self._base_message["TYPE"] = message_type

    def get_type(self):
        return self._base_message['TYPE']

    def get_status(self):
        return self._base_message['STATUS']

    def get_datetime(self):
        return self._base_message['DATETIME']

    def get_username(self):
        return self._base_message['USERNAME']

    def get_body(self):
        return self._base_message['BODY']

    def get_password(self):
        return self._base_message['PASSWORD']

    def serialize(self):
        return dumps(self._base_message)

    def deserialize(self, recv_message):
        self._base_message = loads(recv_message)
