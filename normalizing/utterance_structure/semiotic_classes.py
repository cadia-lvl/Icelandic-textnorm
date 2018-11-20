#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import inspect


class SemioticClasses:

    def __init__(self):
        self.available_classes = [name for name in inspect.getmembers(sys.modules[__name__])]


class Cardinal:

    def __init__(self, val, preserve_ord=False):
        self.name = 'cardinal'
        self.integer = val
        self.preserve_order = preserve_ord

    def __str__(self):
        return 'Cardinal integer: ' + self.integer

    def grammar_attributes(self):
        return [('integer:', self.integer)]

class Ordinal:

    def __init__(self, val, preserve_ord=False):
        self.name = 'ordinal'
        self.integer = val
        self.preserve_order = preserve_ord

    def __str__(self):
        return 'Ordinal integer: ' + self.integer

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

    def grammar_attributes(self):
        return [('hours:', self.hours), ('minutes:', self.minutes)]


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