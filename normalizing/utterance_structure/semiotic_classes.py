#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import inspect


class SemioticClasses:

    def __init__(self):
        self.available_classes = [name for name in inspect.getmembers(sys.modules[__name__])]


#TODO: superclass for semiotic classes?
#TODO: attr_dividor as variable (DIV='|')

class Cardinal:

    def __init__(self, val, preserve_ord=False):
        self.name = 'cardinal'
        self.integer = val
        self.preserve_order = preserve_ord

    def __str__(self):
        return 'Cardinal integer: ' + self.integer

    def serialize_to_string(self):
        return 'cardinal|integer:' + self.integer + '|'

    def grammar_attributes(self):
        return [('integer:', self.integer)]

class Ordinal:

    def __init__(self, val, preserve_ord=False):
        self.name = 'ordinal'
        self.integer = val
        self.preserve_order = preserve_ord

    def __str__(self):
        return 'Ordinal integer: ' + self.integer

    def serialize_to_string(self):
        return 'ordinal|integer:' + self.integer + '|'

    def grammar_attributes(self):
        return [('integer:', self.integer)]

class Decimal:

    def __init__(self, val=None, preserve_ord=False):
        self.name = 'decimal'
        if val and len(val) == 2:
            self.integer_part = val[0]
            self.fractional_part = val[1]
        self.preserve_ord = preserve_ord

    def set_integer_part(self, val):
        self.integer_part = val

    def set_fractional_part(self, val):
        self.fractional_part = val

    def __str__(self):
        return 'Decimal: ' + str(self.grammar_attributes())

    def serialize_to_string(self):
        return 'decimal|integer_part: ' + self.integer_part + ' | fractional_part: ' + self.fractional_part + ' |'

    def grammar_attributes(self):
        return [('integer_part:', self.integer_part), ('fractional_part:', self.fractional_part)]

class Time:

    def __init__(self, val=None, preserve_ord=False):
        self.name = 'time'
        if val and len(val) == 2:
            self.hours = val[0]
            self.minutes = val[1]
        self.preserve_ord = preserve_ord

    def set_hours(self, val):
        self.hours = val

    def set_minutes(self, val):
        self.minutes = val

    def __str__(self):
        return 'Time: ' + str(self.grammar_attributes())

    def serialize_to_string(self):
        return 'time|hours: ' + self.hours + '| minutes: ' + self.minutes + '|'


    def grammar_attributes(self):
        return [('hours:', self.hours), ('minutes:', self.minutes)]

class Date:

    def __init__(self, val=None, preserve_ord=False):
        self.name = 'date'
        if val and len(val) == 2:
            self.day = val[0]
            self.month = val[1]
        self.preserve_ord = preserve_ord

    def set_day(self, val):
        self.day = val

    def set_month(self, val):
        self.month = val

    def __str__(self):
        return 'Date: ' + str(self.grammar_attributes())

    def serialize_to_string(self):
        return 'date|day: ' + self.day + '| month: ' + self.month + '|'

    def grammar_attributes(self):
        return [('day:', self.day), ('month:', self.month)]

class Connector:

    def __init__(self, val=None, preserve_ord=False):
        self.name = 'connector'
        self.from_val = None
        self.to_val = None
        self.connector = None
        preserve_ord = preserve_ord

    def set_from_value(self, val):
        self.from_val = val

    def set_to_value(self, val):
        self.to_val = val

    def set_connector(self, conn):
        self.connector = conn

    def __str__(self):
        return 'Connector: ' + str(self.grammar_attributes())

    def serialize_to_string(self):
        return 'connector|' + self.from_val.serialize_to_string() + ' connector:| ' + self.connector + ' ' \
               + self.to_val.serialize_to_string


    def grammar_attributes(self):
        return [('from_value:', self.from_val), ('connector:', self.connector), ('to_value:', self.to_val)]

class Acronym:

    def __init__(self, val=None, preserve_ord=False):
        self.name = 'acronym'
        if val and len(val) == 2:
            self.head = val[0]
            self.tail = val[1]
        else:
            self.tail = '' # tail attribute is optional for an acronym: 'DVD' vs. 'DVD-diskur'
        self.preserve_ord = preserve_ord

    def set_head(self, val):
        self.head = val

    def set_tail(self, val):
        self.tail = val

    def __str__(self):
        return 'Acronym: ' + str(self.grammar_attributes())

    def serialize_to_string(self):
        return 'acronym|head: ' + self.head + '| tail: ' + self.tail + '|'

    def grammar_attributes(self):
        return [('head:', self.head), ('tail:', self.tail)
                ]


class Abbreviation:

    def __init__(self, val=None, preserve_ord=False):
        self.name = 'abbreviation'
        self.abbr = val
        self.preserve_ord = preserve_ord

    def __str__(self):
        return 'Abbreviation: ' + str(self.grammar_attributes())

    def set_abbreviation(self, val):
        self.abbr = val

    def serialize_to_string(self):
        return 'abbreviation|abbr: ' + self.abbr + '|'

    def grammar_attributes(self):
        return [('abbr:', self.abbr)]


class Percent:

    def __init__(self, val=None, preserve_ord=False):
        self.name = 'percent'
        self.decimal = val
        self.symbol = None

    def __str__(self):
        return 'Percent: ' + str(self.grammar_attributes())

    def set_decimal(self, val):
        self.decimal = val

    def set_symbol(self, sym):
        self.symbol = sym

    def serialize_to_string(self):
        return 'percent|' + self.decimal.serialize_to_string() + ' symbol: ' + self.symbol + '|'

    def grammar_attributes(self):
        return [('decimal:', self.decimal), ('symbol:', self.symbol)]



def main():
    sem = SemioticClasses()
    dec = Decimal(('10', '5'))
    for elem in sem.available_classes:
        if inspect.isclass(elem[1]):
            if isinstance(dec, elem[1]):
                print('Found class: ' + str(elem))
                for attr in dec.grammar_attributes():
                    print('Grammar attr: ' + str(attr))

if __name__ == '__main__':
    main()