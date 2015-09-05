import unittest
import client
import server
import register
from libs.derser import Message
from libs.encrypt_hash import crypto

class RegisterTest(unittest.TestCase):
    def test_set_server(self):
        r = register.Register()
        r.set_server("1.2.3.4", 12345)
        self.assertEqual("1.2.3.4", r._server[0])
        self.assertEqual(12345, r._server[1])

    def test_init(self):
        r = register.Register()
        self.assertEqual(("127.0.0.1", 54555), r._server)

    def test_connection_problems(self):
        r = register.Register()
        try:
            r.close()
        except OSError as err:
            pass
        stat, mesg = r.register("asd", crypto("asd"))
        self.assertFalse(stat)
        self.assertEqual("FAILED", mesg.get_status())
        self.assertEqual("Connection problems", mesg.get_body())
        self.assertEqual("REGISTER", mesg.get_type())

class MessageTest(unittest.TestCase):
    def test_default_constructor(self):
        username = "user"
        type_of_message = "AVATAR"
        m = Message(username, type_of_message)
        self.assertEqual(username, m._base_message["USERNAME"])
        self.assertEqual(type_of_message, m._base_message["TYPE"])

    def test_set_password(self):
        m = Message("", "")
        password = "pass"
        m.set_password(password)
        self.assertEqual(password, m._base_message['PASSWORD'])

    def test_set_body(self):
        m = Message("", "")
        body = "bodyasfniasoflnkas"
        m.set_body(body)
        self.assertEqual(body, m._base_message["BODY"])

    def test_set_status(self):
        m = Message("", "")
        m.set_status()
        self.assertEqual("OK", m._base_message["STATUS"])
        m.set_status("FAILED")
        self.assertEqual("FAILED", m._base_message["STATUS"])

    def set_username(self):
        m = Message("", "")
        username = "asdadsad"
        m.set_username(username)
        self.assertEqual(username, m._base_message["USERNAME"])

    def test_set_type(self):
        m = Message("", "")
        type = "LIKE"
        m.set_type(type)
        self.assertEqual(type, m._base_message["TYPE"])

    def test_getters(self):
        username = "Username"
        password = "pasd"
        stat = "OK"
        type_mesg = "LOGOUT"
        body = "snodjk"
        m = Message(username, type_mesg)
        m.set_status(stat)
        m.set_password(password)
        m.set_body(body)
        self.assertEqual(username, m.get_username())
        self.assertEqual(password, m.get_password())
        self.assertEqual(stat, m.get_status())
        self.assertEqual(type_mesg, m.get_type())
        self.assertEqual(body, m.get_body())

    def test_der_ser(self):
        username = "Username"
        password = "pasd"
        stat = "OK"
        type_mesg = "LOGOUT"
        body = "snodjk"
        m = Message(username, type_mesg)
        m.set_status(stat)
        m.set_password(password)
        m.set_body(body)
        ser = m.serialize()
        der = Message("", "")
        der.deserialize(ser)
        self.assertEqual(m.get_body(), der.get_body())
        self.assertEqual(m.get_type(), der.get_type())
        self.assertEqual(m.get_status(), der.get_status())
        self.assertEqual(m.get_datetime(), der.get_datetime())
        self.assertEqual(m.get_password(), der.get_password())
        self.assertEqual(m.get_username(), der.get_username())

class ClientTest(unittest.TestCase):
    def test_set_server(self):
        addr , port = "4.5.6.6", 12332
        cl = client.Client()
        cl.set_server(addr, port)
        self.assertEqual(addr, cl._server[0])
        self.assertEqual(port, cl._server[1])

    def test_default_server(self):
        cl = client.Client()
        self.assertEqual("127.0.0.1", cl._server[0])
        self.assertEqual(54554, cl._server[1])

class ServerTest(unittest.TestCase):
    def test_constructor(self):
        s = server.Server()
        self.assertEqual(s.db_addr, "127.0.0.1")
        self.assertEqual(s.db_port, 27017)
        self.assertIsNone(s.db_client)

    def test_is_connected_to_db(self):
        '''
        This test rely on not working MongoDb on 127.0.0.1:27017
        '''
        s = server.Server()
        s.connect_to_db()
        self.assertFalse(s.is_connected_to_db())




if __name__ == "__main__":
    unittest.main()