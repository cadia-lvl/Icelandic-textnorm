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
            self.assertEqual(tuple[1], normalized)

    def init_test_tuples(self, test_data):
        test_tuples = []
        for line in test_data.read().splitlines():
            if line.startswith('#') or line == '':
                continue
            test_tuples.append(tuple(line.split('\t')))

        return test_tuples
