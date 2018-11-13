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
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            norm.print_normalized_text()
            self.assertEqual(tuple[1], normalized)

    def test_unk(self):
        #TODO: recover <unk>
        test_tuple = ('5 þettaorðerekkitil', 'fimm þettaorðerekkitil')
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir)
        normalized = norm.normalize(test_tuple[0])
        norm.print_normalized_text()
        self.assertEqual(test_tuple[1], normalized)

    def test_date_normalizer(self):
        test_tuples = self.get_date_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            norm.print_normalized_text()
            #self.assertEqual(tuple[1], normalized)


    def get__basic_cardinal_test_tuples(self):
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

    def get_cardinal_test_tuples(self):
        tuple_list = []
        tuple_list.append(('04', 'núll fjórum'))#'núll fjórir')) - need to set nominative as default when no context
        tuple_list.append(('5000 pund', 'fimm þúsund pund'))
        tuple_list.append(('bjóða 1200 börnum', 'bjóða tólf hundruð börnum'))
        tuple_list.append((('um 20000 stuðningsmenn', 'um tuttugu þúsund stuðningsmenn')))
        tuple_list.append(('að 54 börn', 'að fimmtíu og fjögur börn'))
        tuple_list.append(('núna í 18777 silungum', 'núna í átján þúsund sjö hundruð sjötíu og sjö silungum'))
        tuple_list.append(('núna í 18770 silungum', 'núna í átján þúsund sjö hundruð og sjötíu silungum'))
        tuple_list.append(('18700 silungar', 'átján þúsund og sjö hundruð silungar'))
        tuple_list.append(('2 milljarða', 'tvo milljarða'))
        tuple_list.append(('fékk síðan 902 milljarða', 'fékk síðan níu hundruð og tvo milljarða'))
        #tuple_list.append(('spilaði samtals 199 leiki', 'spilaði samtals eitt hundrað níutíu og níu leiki'))
        tuple_list.append(('sem er 21 prósent skotnýting', 'sem er tuttugu og eitt prósent skotnýting'))
        tuple_list.append(('með að skora 21 stig', 'með að skora tuttugu og eitt stig'))
        tuple_list.append(('21 kona', 'tuttugu og ein kona'))
        tuple_list.append(('eftir 21 leik', 'eftir tuttugu og einn leik'))
        tuple_list.append(('sem er 21 árs', 'sem er tuttugu og eins árs'))
        tuple_list.append(('er 4 ára gamall', 'er fjögurra ára gamall'))
        tuple_list.append(('er 54 ára gamall', 'er fimmtíu og fjögurra ára gamall'))
        tuple_list.append(('næstum því 54 milljónir', 'næstum því fimmtíu og fjórar milljónir'))
        tuple_list.append(('tæplega 54 prósent atkvæða', 'tæplega fimmtíu og fjögur prósent atkvæða'))
        tuple_list.append(('spilaði 54 leiki', 'spilaði fimmtíu og fjóra leiki'))


        return tuple_list


    def get_ordinal_test_tuples(self):
        tuple_list = []
        tuple_list.append(('1. janúar', 'fyrsta janúar'))
        tuple_list.append(('2. febrúar', 'öðrum febrúar'))
        tuple_list.append(('3. mars', 'þriðja mars'))
        tuple_list.append(('4. apríl', 'fjórða apríl'))

        return tuple_list

    def get_date_test_tuples(self):
        tuple_list = []
        #tuple_list.append(('taka gildi 1. janúar 2019', 'taka gildi fyrsta janúar'))
        tuple_list.append(('taka gildi 1. janúar 1900', 'taka gildi fyrsta janúar'))
        tuple_list.append(('taka gildi 1. janúar 1905', 'taka gildi fyrsta janúar'))
        tuple_list.append(('taka gildi 1. janúar 1910', 'taka gildi fyrsta janúar'))

        tuple_list.append(('taka gildi 1. janúar 1925', 'taka gildi fyrsta janúar'))

        tuple_list.append(('taka gildi 1. janúar 2000', 'taka gildi fyrsta janúar'))
        tuple_list.append(('taka gildi 1. janúar 2005', 'taka gildi fyrsta janúar'))
        tuple_list.append(('taka gildi 1. janúar 2010', 'taka gildi fyrsta janúar'))

        tuple_list.append(('taka gildi 1. janúar 2044', 'taka gildi fyrsta janúar'))

        return tuple_list

    def get_tel_test_tuples(self):
        tuple_list = []
        tuple_list.append('í síma 861 9401', 'í síma átta sex einn níu fjórir núll einn')
    def get_unk_test_tuples(self):
        tuple_list = []
        tuple_list.append(('að 54 aðildarsambönd', 'að fimmtíu og fjögur aðildarsambönd'))

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

