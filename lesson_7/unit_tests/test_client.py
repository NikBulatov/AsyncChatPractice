import sys
import unittest

sys.path.append("../")

from variables import (RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME,
                       ACTION, PRESENCE)
from services import create_presence, process_answer


class TestClass(unittest.TestCase):

    def test_create_presence(self):
        test = create_presence()
        test[TIME] = 123456.32165
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 123456.32165,
                                USER: {ACCOUNT_NAME: "Guest"}})

    def test_200_ans(self):
        self.assertEqual(process_answer({RESPONSE: 200}), "200 : OK")

    def test_400_ans(self):
        self.assertEqual(process_answer({RESPONSE: 400, ERROR: "Bad Request"}),
                         "400 : Bad Request")

    def test_no_response(self):
        self.assertRaises(ValueError, process_answer, {ERROR: "Bad Request"})


if __name__ == "__main__":
    unittest.main()
