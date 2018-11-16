#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classify an utterance according to a Thrax classifying grammar


"""
import pynini as pn
from fst_compiler import FST_Compiler


class Classifier:

    SPACE = '0x0020'

    def __init__(self, path_to_grammar, utf8_symbols):
        try:
            self.thrax_grammar = pn.Fst.read(path_to_grammar)
            self.thrax_grammar.arcsort()
            self.utf8_symbols = utf8_symbols
        except IOError:
            #TODO: logging
            print('Could not read grammar from: ' + path_to_grammar)


    def classify(self, text):
        """
        Classifies text according to the thrax grammar. Returns both an FST representing the classification,
        and a string version.

        :param text:
        :return: an FST and a string representation of the classified text
        """

        classified_fst = self._create_classified_fst(text)
        classified_string = self._create_classified_string(classified_fst).replace('<epsilon>', '')

        return classified_fst, classified_string


    def _create_classified_fst(self, text):

        compiler = FST_Compiler(self.utf8_symbols, None)
        inp_fst = compiler.fst_stringcompile(text)
        all_fst = pn.compose(inp_fst, self.thrax_grammar)
        all_fst.draw('all_class.dot')
        shortest_path = pn.shortestpath(all_fst).optimize()
        shortest_path.draw('shortes_class.dot')
        shortest_path.rmepsilon()

        return shortest_path

    def _create_classified_string(self, classified_fst):

        classified = classified_fst.stringify(token_type=self.utf8_symbols)
        # the classified results are character based, combine the chars to words again
        classified = classified.replace(' ', '')
        # the real word separators are encoded with unicode representation of SPACE, replace that with ' '
        classified = classified.replace(self.SPACE, ' ')

        return classified

