import unittest
import sys
import os

sys.path.append(os.path.join(os.getcwd(), '../..'))
from lesson_3.task_1.server import parse_client_message


class TestGetClientMessage(unittest.TestCase):
    resp_ok = '{"response": 200}'
    resp_err = '{"response": 400, "error": "Bad request"}'

    def test_no_action_field(self):
        self.assertEqual(parse_client_message(
            {"time": 1232.5434, "user": {"name": "Guest"}}), self.resp_err)

    def test_wrong_action_field(self):
        self.assertEqual(parse_client_message(
            {"action": 'Wrong', "time": 1232.5434, "user": {"name": "Guest"}}), self.resp_err)

    def test_no_time_field(self):
        self.assertEqual(parse_client_message(
            {"action": 'Wrong', "user": "Guest"}), self.resp_err)

    def test_no_user_data(self):
        self.assertEqual(parse_client_message(
            {"action": 'Wrong', "time": 1232.5434}), self.resp_err)

    def test_unknown_user_data(self):
        self.assertEqual(parse_client_message(
            {"action": 'Wrong', "time": 1232.5434, "user": {"name": "GuestUnknown"}}), self.resp_err)

    def test_correct_data(self):
        self.assertEqual(parse_client_message(
            {"action": 'presence', "time": 1232.5434, "user": {"name": "Guest"}}), self.resp_ok)


if __name__ == '__main__':
    unittest.main()
