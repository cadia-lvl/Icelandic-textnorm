#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classify an utterance according to a Thrax classify grammar


"""
import pynini as pn
import pywrapfst as fst
from fst_compiler import FST_Compiler

class Classifier:

    def __init__(self, path_to_grammar='/Users/anna/sparrowhawk/sparrowhawk/documentation/grammars/ice/classify/TOKENIZE_AND_CLASSIFY'):
        self.thrax_grammar = pn.Fst.read(path_to_grammar)
        self.thrax_grammar.arcsort()

    def classify(self, text):
        compiler = FST_Compiler()
        inp_fst = compiler.fst_stringcompile(text)
        all_fst = pn.compose(inp_fst, self.thrax_grammar)
        shortest_path = pn.shortestpath(all_fst).optimize()

        classified = shortest_path.stringify(token_type=compiler.utf8_symbols)
        classified = classified.replace(' ', '')
        classified = classified.replace('0x0020', ' ')
        return shortest_path, classified


def main():
    classifier = Classifier()

    print(classifier.classify("af þessum 5 atriðum"))


if __name__ == '__main__':
    main()
