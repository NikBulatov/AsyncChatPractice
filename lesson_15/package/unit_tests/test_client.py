import sys
import unittest

sys.path.append("../../")

from services.errors import ServerError, NonDictionaryInputError
from services.variables import (
    RESPONSE,
    ERROR,
    USER,
    ACCOUNT_NAME,
    TIME,
    ACTION,
    PRESENCE,
)
from services.services import create_presence, process_server_response


class TestClass(unittest.TestCase):
    def test_create_presence(self):
        test = create_presence()
        test[TIME] = 123456.32165
        self.assertEqual(
            test, {ACTION: PRESENCE, TIME: 123456.32165, USER: {ACCOUNT_NAME: "Guest"}}
        )

    def test_200_ans(self):
        self.assertEqual(process_server_response({RESPONSE: 200}), "200 : OK")

    def test_400_ans(self):
        self.assertRaises(
            ServerError, process_server_response, {RESPONSE: 400, ERROR: "Bad Request"}
        )

    def test_no_response(self):
        self.assertRaises(
            NonDictionaryInputError, process_server_response, "{400: 'Bad request'}"
        )


if __name__ == "__main__":
    unittest.main()
