import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '../..'))
from lesson_3.task_1.client import create_presence, process_answer


class TestClass(unittest.TestCase):
    def test_def_presence(self):
        test = eval(create_presence())
        test["time"] = 1232.5434
        self.assertEqual(test, {"action": "presence", "time": 1232.5434, "user": {"name": 'Guest'}})

    def test_200_ans(self):
        self.assertEqual(process_answer({"response": 200}), '200 : OK')

    def test_400_ans(self):
        self.assertEqual(process_answer({"response": 400, "error": 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        self.assertRaises(ValueError, process_answer, {"error": 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
