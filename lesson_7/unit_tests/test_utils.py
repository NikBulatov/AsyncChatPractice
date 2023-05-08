import json
import unittest
import sys

sys.path.append("../")

from variables import (RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION,
                       PRESENCE, ENCODING)


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_msg = None
        self.received_msg = None

    def send(self, message_to_send):
        json_test_msg = json.dumps(self.test_dict)
        self.encoded_msg = json_test_msg.encode(ENCODING)
        self.received_msg = message_to_send

    def recv(self, max_len):
        json_msg = json.dumps(self.test_dict)
        return json_msg.encode(ENCODING)


class Tests(unittest.TestCase):
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 123545.123,
        USER: {
            ACCOUNT_NAME: "test_name"
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: "Bad Request"
    }

    def test_send_message(self):
        test_socket = TestSocket(self.test_dict_send)
        test_socket.send(self.test_dict_send)
        self.assertEqual(eval(test_socket.encoded_msg.decode(ENCODING)),
                         test_socket.received_msg)
        with self.assertRaises(Exception):
            json_msg = json.dumps(test_socket)
            test_socket.send(json_msg)

    def test_get_message(self):
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)

        resp_ok = test_sock_ok.recv(4096)
        self.assertEqual(eval(resp_ok.decode(ENCODING)), self.test_dict_recv_ok)

        resp_err = test_sock_err.recv(4096)
        self.assertEqual(eval(resp_err.decode(ENCODING)),
                         self.test_dict_recv_err)


if __name__ == "__main__":
    unittest.main()
