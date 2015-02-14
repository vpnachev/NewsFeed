'''
This is simple serialize/deserialize lib/

It convert builtin.dict to stringed json -> serialize
and vice versa
stringed json do dict -> deserialize
'''
from json import dumps, loads

def serialize(dict_arg):
    return dumps(dict_arg, ensure_ascii=False)

def deserialize(str_arg):
    return loads(str_arg)

class Message:
    def __init__(self, type, date, status, username="", password="", body=""):
        self.type = type
        self.date = date
        self.status = status
        self.username = username
        self.password = password
        self.body = body

    def deserialize(self, json_str):
        ders = deserialize(json_str)
        self.type = ders["type"]
        self.date = ders["date"]
        self.status = ders["status"]
        self.username = ders["username"]
        self.password = ders["password"]
        self.body = ders["body"]

    def serialize(self):
        return  serialize({"type": self.type, "date": self.date, "status":self.status,
                "username": self.username, "password": self.password, "body": self.body})



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