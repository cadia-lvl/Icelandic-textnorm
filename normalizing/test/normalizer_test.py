import unittest
import os
from normalizing.expand_numbers import Expander

from normalizing.normalizer import Normalizer

class TestNormalizer(unittest.TestCase):

    def test_cardinal_normalizer(self):
        test_tuples = self.get_cardinal_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            #print(normalized)
            self.assertEqual(tuple[1], normalized)

    def test_ordinal_normalizer(self):
        test_tuples = self.get_ordinal_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir)
       # for tuple in test_tuples:
       #     normalized = norm.normalize(tuple[0])
       #     norm.print_normalized_text()
            #self.assertEqual(tuple[1], normalized)


    def get_cardinal_test_tuples(self):
        tuple_list = []
        tuple_list.append(('þessi 2 börn', 'þessi tvö börn'))
        tuple_list.append(('þessar 2 konur', 'þessar tvær konur'))
        tuple_list.append(('þessir 2 menn', 'þessir tveir menn'))
        tuple_list.append(('þessi 3 börn', 'þessi þrjú börn'))
        tuple_list.append(('þessar 3 konur', 'þessar þrjár konur'))
        tuple_list.append(('þessir 3 menn', 'þessir þrír menn'))
        tuple_list.append(('þessi 4 börn', 'þessi fjögur börn'))
        tuple_list.append(('þessar 4 konur', 'þessar fjórar konur'))
        tuple_list.append(('þessir 4 menn', 'þessir fjórir menn'))

        return tuple_list

    def get_ordinal_test_tuples(self):
        tuple_list = []
        tuple_list.append(('1. janúar', 'fyrsti janúar'))

        return tuple_list


    """
    def test_normalizing(self):
        original = open('lvl_tts_training.txt')
        normalized = open('lvl_tts_training_norm_lower.txt')

        normalized_dict = {}
        for line in normalized.readlines():
            utt_id, utt = line.split('\t')
            normalized_dict[utt_id] = utt.strip()

        normalizer = Expander('/Users/anna/PycharmProjects/text_normalization/normalizing/expander.conf')

        for line in original.readlines():
            utt_id, utt = line.split('\t')
            norm = normalizer.normalize(utt)
            self.assertEqual(normalized_dict[utt_id], norm)
    """

