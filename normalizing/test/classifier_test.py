import unittest
import os
from normalizing.expand_numbers import Expander

from normalizing.normalizer import Normalizer

#TODO: disambiugation mechanism for time vs. sports_results (23:22 - time or handball result?)
# Join in one file and put extra weight on sports results for now?

class TestClassifier(unittest.TestCase):

    def test_cardinal_classifier(self):
        test_tuples = self.get_basic_decimal_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir, verbalize=False)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            #print(normalized)
            self.assertEqual(tuple[1], normalized)

    def test_ordinal_classifier(self):
        test_tuples = self.get_ordinal_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir, verbalize=False)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            #print(normalized)
            self.assertEqual(tuple[1], normalized)

    @unittest.skip('skip for now')
    def test_time_classifier(self):
        test_tuples = self.get_time_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir, verbalize=False)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            #print(normalized)
            self.assertEqual(tuple[1], normalized)

    def test_date_classifier(self):
        test_tuples = self.get_date_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir, verbalize=False)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            #print(normalized)
            self.assertEqual(tuple[1], normalized)

    def test_thousand_classifier(self):
        test_tuples = self.get_thousand_dot_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir, verbalize=False)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            #print(normalized)
            self.assertEqual(tuple[1], normalized)

    def test_time_sports_classifier(self):
        test_tuples = self.get_time_sports_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir, verbalize=False)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            #print(normalized)
            self.assertEqual(tuple[1], normalized)

    def test_sports_results_classifier(self):
        test_tuples = self.get_sports_results_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir, verbalize=False)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            # print(normalized)
            self.assertEqual(tuple[1], normalized)

    def test_connector_classifier(self):
        test_tuples = self.get_connectors_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir, verbalize=False)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            # print(normalized)
            self.assertEqual(tuple[1], normalized)

    def test_pron_symbol_classifier(self):
        test_tuples = self.get_symbols_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir, verbalize=False)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            # print(normalized)
            self.assertEqual(tuple[1], normalized)

    def test_non_pron_symbol_classifier(self):
        test_tuples = self.get_non_pron_symbols_test_tuples()
        normalizer_dir = os.getcwd()[:-4]
        norm = Normalizer(working_dir=normalizer_dir, verbalize=False)
        for tuple in test_tuples:
            normalized = norm.normalize(tuple[0])
            # print(normalized)
            self.assertEqual(tuple[1], normalized)

    def get_ordinal_test_tuples(self):
        #63. 42. 211. 51. 101.
        tuple_list = []
        tuple_list.append(('63. kom', 'tokens { ordinal { integer: "63" } } tokens { name: "kom" }'))
        tuple_list.append(('101. kom', 'tokens { ordinal { integer: "101" } } tokens { name: "kom" }'))

        return tuple_list

    def get_basic_decimal_test_tuples(self):
        tuple_list = []
        tuple_list.append(('10,5', 'tokens { decimal { integer_part: "10" fractional_part: "5" } }'))
        tuple_list.append(('72,38', 'tokens { decimal { integer_part: "72" fractional_part: "38" } }'))
        tuple_list.append(('38,0', 'tokens { decimal { integer_part: "38" fractional_part: "0" } }'))
        tuple_list.append(('5,351', 'tokens { decimal { integer_part: "5" fractional_part: "351" } }'))
        tuple_list.append(('2,06', 'tokens { decimal { integer_part: "2" fractional_part: "06" } }'))

        return tuple_list

    def get_time_test_tuples(self):
        tuple_list = []
        #11:20 15:58 03:00 2:39 10:00 01:00 (klukkan) 17.30 (klukkan) 2.30 11.00 9:04 16:04
        tuple_list.append(('11:20', 'tokens { time { hours: "11" minutes: "20" } }'))
        tuple_list.append(('15:58', 'tokens { time { hours: "15" minutes: "58" } }' ))
        tuple_list.append(('03:00', 'tokens { time { hours: "03" minutes: "00" } }'))
        tuple_list.append(('01:00', 'tokens { time { hours: "01" minutes: "00" } }'))
        tuple_list.append(('2:39', 'tokens { time { hours: "2" minutes: "39" } }'))

        return tuple_list

    def get_date_test_tuples(self):
        tuple_list = []
        #06.05(.) 10.08(.) 16.7(.) 11.7 26.5. 23.8.
        tuple_list.append(('06.05. kom', 'tokens { date { day: "06" month: "05" } } tokens { name: "kom" }'))
        tuple_list.append(('10.08. kom', 'tokens { date { day: "10" month: "08" } } tokens { name: "kom" }' ))
        tuple_list.append(('16.7. kom', 'tokens { date { day: "16" month: "7" } } tokens { name: "kom" }'))
        tuple_list.append(('23.12. kom', 'tokens { date { day: "23" month: "12" } } tokens { name: "kom" }'))
        tuple_list.append(('43.52. kom', 'tokens { name: "43.52" } tokens { name: "." pause_length: PAUSE_LONG phrase_break: true type: PUNCT } tokens { name: "kom" }'))

        return tuple_list

    def get_thousand_dot_test_tuples(self):
        # 8.400 6.500 34.700 4.189.000 145.000 9.990 900.000 1.900
        # 4.590 343.960 10.350.000 1.750.000 1.651.002 1.754.072 178.985.000 25.000.000

        #TODO: delete dots already while classifying?
        tuple_list = []
        tuple_list.append(('8.400', 'tokens { cardinal { integer: "8.400" } }'))
        tuple_list.append(('34.700', 'tokens { cardinal { integer: "34.700" } }'))
        tuple_list.append(('4.189.000', 'tokens { cardinal { integer: "4.189.000" } }'))
        tuple_list.append(('178.985.000', 'tokens { cardinal { integer: "178.985.000" } }'))

        return tuple_list

    def get_time_sports_test_tuples(self):
        # 3:27:40 33:06

        tuple_list = []
        tuple_list.append(('3:27:40', 'tokens { time_sports { hours: "3" minutes: "27" seconds: "40" } }'))
        tuple_list.append(('33:06', 'tokens { time_sports { minutes: "33" seconds: "06" } }'))

        return tuple_list

    def get_sports_results_test_tuples(self):

        #9:0 15:11 39:36 4:3 81:66 23:22 5:1
        tuple_list = []
        tuple_list.append(('9:0', 'tokens { sports_results { home: "9" guests: "0" } }'))
        tuple_list.append(('81:66', 'tokens { sports_results { home: "81" guests: "66" } }'))

        return tuple_list

    def get_connectors_test_tuples(self):

        #2018-2022 1989-1994 1.500-2.000 9-12 20.-30. 7-8
        #7.-9. 1.-10. 100-350
        tuple_list = []
        tuple_list.append(('2018-2022', 'tokens { connector { cardinal { integer: "2018" } connector: "-" cardinal { integer: "2022" } } }'))
        tuple_list.append(('1.500-2.000', 'tokens { connector { cardinal { integer: "1.500" } connector: "-" cardinal { integer: "2.000" } } }'))
        tuple_list.append(('7.-9. des', 'tokens { connector { ordinal { integer: "7" } connector: "-" ordinal { integer: "9" } } } tokens { name: "des" }'))

        return tuple_list

    def get_symbols_test_tuples(self):
        # 200° 7% 6,5%
        tuple_list = []
        tuple_list.append(('-0,6', 'tokens { negative { symbol: "-" decimal { integer_part: "0" fractional_part: "6" } } }'))
        tuple_list.append(('200°', 'tokens { degrees { cardinal { integer: "200" } symbol: "°" } }'))
        tuple_list.append(('7%', 'tokens { percent { cardinal { integer: "7" } symbol: "%" } }'))
        tuple_list.append(('6,5%', 'tokens { percent { decimal { integer_part: "6" fractional_part: "5" } symbol: "%" } }'))

        return tuple_list

    def get_non_pron_symbols_test_tuples(self):
        # 569-1122 0513-14-406615 17-18-22-26-33-34
        tuple_list = []
        tuple_list.append(('569-1122', 'tokens { telephone { cardinal { integer: "569" } cardinal { integer: "1122" } } }'))
        tuple_list.append(('0513-14-406615', 'tokens { bank_account { cardinal { integer: "0513" } cardinal { integer: "14" } cardinal { integer: "406615" } } }'))
        tuple_list.append(('17-18-22-26-33-34', 'tokens { number_row { cardinal { integer: "17" } cardinal { integer: "18" } '
                                                'cardinal { integer: "22" } cardinal { integer: "26" } cardinal { integer: "33" }'
                                                ' cardinal { integer: "34" } } }'))
        return tuple_list
