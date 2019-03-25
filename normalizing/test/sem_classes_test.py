import unittest
import os

from utterance_structure.semiotic_classes import *

class TestSemClasses(unittest.TestCase):

    def test_cardinal_class(self):
        sem = SemioticClasses('cardinal').semiotic_class
        tup = ('integer:', 5)
        sem.set_attribute(tup)
        self.assertEqual('cardinal|integer: 5 |', sem.serialize_to_string())

    def test_ordinal_class(self):
        sem = SemioticClasses('ordinal').semiotic_class
        tup = ('integer:', 5)
        sem.set_attribute(tup)
        self.assertEqual('ordinal|integer: 5 |', sem.serialize_to_string())

    def test_decimal_class(self):
        sem = SemioticClasses('decimal').semiotic_class
        tup1 = ('integer_part:', 5)
        sem.set_attribute(tup1)
        tup2 = ('fractional_part:', 7)
        sem.set_attribute(tup2)
        self.assertEqual('decimal|integer_part: 5 | fractional_part: 7 |', sem.serialize_to_string())

    def test_time_class(self):
        sem = SemioticClasses('time').semiotic_class
        tup1 = ('hours:', 13)
        sem.set_attribute(tup1)
        tup2 = ('minutes:', 30)
        sem.set_attribute(tup2)
        self.assertEqual('time|hours: 13 | minutes: 30 |', sem.serialize_to_string())

    def test_date_class(self):
        sem = SemioticClasses('date').semiotic_class
        tup1 = ('day:', '8')
        tup2 = ('month:', '12')
        tup3 = ('year:', '2010')
        sem.set_attribute(tup1)
        sem.set_attribute(tup2)
        self.assertEqual('date|day: 8 | month: 12 |', sem.serialize_to_string())
        sem.set_attribute(tup3)
        self.assertEqual('date|day: 8 | month: 12 | year: 2010 |', sem.serialize_to_string())

    def test_connector_class(self):
        sem = SemioticClasses('connector').semiotic_class
        VALID_LABELS = ['cardinal', 'ordinal', 'decimal', 'date', 'time']
        CONN = 'connector:'
        card1 = ('integer:', 5)
        card2 = ('integer:', 10)
        conn = ('sym:', '-')
        sem.set_attribute(card1, label='cardinal')
        sem.set_attribute(card2, label='cardinal')
        sem.set_attribute(conn)
        self.assertEqual('connector|cardinal|integer: 5 | conn|sym: - | cardinal|integer: 10 |', sem.serialize_to_string())

        tup1 = ('day:', '8')
        tup2 = ('month:', '12')
        tup3 = ('year:', '2010')
        tup4 = ('day:', '18')
        sem = SemioticClasses('connector').semiotic_class
        sem.set_attribute(tup1, label='date')
        sem.set_attribute(tup2, label='date')
        sem.set_attribute(tup3, label='date')
        sem.set_attribute(conn)
        sem.set_attribute(tup4, label='date')
        sem.set_attribute(tup2, label='date')
        sem.set_attribute(tup3, label='date')
        self.assertEqual('connector|date|day: 8 | month: 12 | year: 2010 | conn|sym: - | date|day: 18 | month: 12 | year: 2010 |',
                         sem.serialize_to_string())

    def test_connector_fails(self):
        tup1 = ('day:', '8')
        tup2 = ('month:', '12')
        tup3 = ('year:', '2010')
        conn = ('sym:', '-')
        sem = SemioticClasses('connector').semiotic_class
        sem.set_attribute(tup1, label='date')
        sem.set_attribute(tup2, label='date')
        sem.set_attribute(tup3, label='date')
        sem.set_attribute(conn)
        with self.assertRaises(ValueError):
            sem.set_attribute(('integer:', 5), label='cardinal')

    def test_acronym_class(self):
        sem = SemioticClasses('acronym').semiotic_class
        tup1 = ('head:', 'ACRONYM')
        tup2 = ('tail:', 'normalword')
        sem.set_attribute(tup1)
        self.assertEqual('acronym|head: ACRONYM |', sem.serialize_to_string())
        sem.set_attribute(tup2)
        self.assertEqual('acronym|head: ACRONYM | tail: normalword |', sem.serialize_to_string())

    def test_abbreviation_class(self):
        sem = SemioticClasses('abbreviation').semiotic_class
        tup = ('abbr:', 't.d.')
        sem.set_attribute(tup)
        self.assertEqual('abbreviation|abbr: t.d. |', sem.serialize_to_string())

    def test_percent_class(self):
        sem = SemioticClasses('percent').semiotic_class
        tup1 = ('integer_part:', 5)
        tup2 = ('fractional_part:', 7)
        sym = ('symbol:', '%')
        sem.set_attribute(tup1, label='decimal')
        sem.set_attribute(tup2, label='decimal')
        sem.set_attribute(sym)
        self.assertEqual('percent|decimal|integer_part: 5 | fractional_part: 7 | per|symbol: % |', sem.serialize_to_string())
