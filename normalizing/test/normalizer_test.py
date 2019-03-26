import unittest
import os
from normalizing.expand_numbers import Expander

from normalizing.normalizer import Normalizer

class TestNormalizer(unittest.TestCase):

    TEST_FILE = 'normalizer_testdata.txt'

    def test_normalizer(self):
        test_data = open(self.TEST_FILE)
        test_tuples = self.init_test_tuples(test_data)
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            print(normalized)
            self.assertTrue(normalized in tuple[1])

    def init_test_tuples(self, test_data):
        test_tuples = []
        for line in test_data.read().splitlines():
            if line.startswith('#') or line == '':
                continue
            test_arr = line.split('\t')
            if len(test_arr) != 2:
                print(line + ' does not have the correct format!')

            test_tuples.append((test_arr[0], test_arr[1].split('|')))

        test_data.close()

        return test_tuples
