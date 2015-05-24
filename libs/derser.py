'''
This is simple serialize/deserialize lib/

It convert builtin.dict to stringed json -> serialize
and vice versa
stringed json do dict -> deserialize
'''
from json import dumps, loads
import time

def serialize(dict_arg):
    return dumps(dict_arg, ensure_ascii=False)

def deserialize(str_arg):
    return loads(str_arg)


class Message:
    def __init__(self,username, type_of_message):
        self._base_message = dict(TYPE=type_of_message, USERNAME=username)
        self._base_message["DATETIME"] = time.asctime(time.gmtime())

    def set_password(self, password):
        ''' here password is already hashed with sha256'''
        self._base_message['PASSWORD']=password

    def set_body(self, body):
        ''' Here body is the text of message or content of transmitted file'''
        self._base_message['BODY']=body

    def set_status(self, status='OK'):
        self._base_message['STATUS'] = status

    def set_chunk_number(self, current_chunk, all_chunks):
        self._base_message['CHUNK_NUMBER'] = (current_chunk,all_chunks)

    def set_name_of_file(self, filename):
        self._base_message["FILENAME"] = filename

    def set_datetime(self):
        self._base_message["DATETIME"] = time.asctime(time.gmtime())

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

    def get_chunk_number(self):
        return  self._base_message['CHUNK_NUMBER']

    def get_filename(self):
        return self._base_message['FILENAME']

    def serialize(self):
        return dumps(self._base_message)

    def deserialize(self, recv_message):
        self._base_message = loads(recv_message)


'''
MESSAGE INTERFACE
{
    "TYPE": ["REGISTER", "LOGIN", "LOGOUT", "SYNC", "MESSAGE", "LIKE", "BLOCK", "20_MORE", "AVATAR", "RATING", "FILE"],
    "DATETIME": ["15:43:55/14.02.2015] -> utc time/gmt+00
    "STATUS": ["OK", "FAILED"],
    "USERNAME": "login/register username",
    "PASSWORD": "password, used only for authentication and registration",
    "BODY": "TEXT"/"content of file"
    "CHUNK_NUMBER" : current_part/all_parts(11/23 - 11 piece of File devided into 23 parts)
    "FILENAME" : "hello_world.txt"t
}'''