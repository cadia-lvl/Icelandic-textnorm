import unittest

from normalizing.expand_numbers import Expander

class TestNormalizer(unittest.TestCase):

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

