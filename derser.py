'''
This is simple serialize/deserialize lib/

It convert builtin.dict to stringed json -> serialize
and vice versa
stringed json do dict -> deserialize
'''
from json import dumps, load

def serialize(dict_arg):
    return dumps(dict_arg, ensure_ascii=False)

def deserialize(str_arg):
    return load(str_arg)

'''

MESSAGE INTERFACE
{
    "type": ["REG", "LOGIN", "LOGOUT", "SYNC", "MESG", "LIKE", "BLOCK", "20 MORE", "AVATAR", "RATING"],
    "date": ["15:43:55/14.02.2015]  -> utc time/gmt+00
    "status": ["OK", "FAILED"],
    "username": "login/register username, ",
    "password": "password, used only for authentication and registration",
    "body": "TEXT"
}'''