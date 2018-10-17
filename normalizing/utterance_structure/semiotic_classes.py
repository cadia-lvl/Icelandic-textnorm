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


def main():
    sem = SemioticClasses()
    card = Cardinal('10')
    for elem in sem.available_classes:
        if inspect.isclass(elem[1]):
            if isinstance(card, elem[1]):
                print('Found class: ' + str(elem))
                for attr in card.grammar_attributes():
                    print('Grammar attr: ' + str(attr))

if __name__ == '__main__':
    main()