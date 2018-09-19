#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright: Reykjavik University
Author: Anna Björk Nikulásdóttir
License: Apache 2.0

Expands numbers in an input text according to a given grammar and a language model, stored in a configuration file.

Example:

    input: 'þetta eru 2 konur'
    output: 'þetta eru tvær konur'

Make sure that you have already run expander_config.py (and adapted according to your models)

"""

import sys
import configparser
import re
import queue
import pynini as pn
import pywrapfst as fst


class Expander:

    def __init__(self, configfile):
        config = configparser.ConfigParser()
        config.read(configfile)
        grammar_dir = config['GRAMMAR_DIRS']['grammars']
        utf8_symfile = grammar_dir + config['symbol tables']['utf8']
        word_symfile = grammar_dir + config['symbol tables']['word-symbol']
        exp_grammarfile = grammar_dir + config['models']['grammar']
        lm_file = grammar_dir + config['models']['language model']

        self.utf8_symbols = pn.SymbolTable.read_text(utf8_symfile)
        self.word_symbols = pn.SymbolTable.read_text(word_symfile)
        self.exp_grammar = pn.Fst.read(exp_grammarfile)
        self.exp_grammar.arcsort()
        print("reading LM file ...")
        self.LM = pn.Fst.read(lm_file)
        print("initialized LM")
        self.LM.set_input_symbols(self.word_symbols)
        self.LM.set_output_symbols(self.word_symbols)
        self.LM.arcsort()

    def should_expand(self, token):

        if token.isdigit():
            return True
        if re.match('\d+\.', token):
            return True

    def clean(self, text):
        """
        Prepare for FST building.
        a) replace OOV words with '<word>'. Keep track so we can rebuild the original text.
        :param text:
        :return:
        """
        self.current_oov_queue = queue.Queue()
        text_arr = text.split()
        for ind, wrd in enumerate(text_arr):
            sym = self.word_symbols.find(wrd)
            if sym == -1 and not self.should_expand(wrd):
                self.current_oov_queue.put(wrd)
                text_arr[ind] = 'x'

        return ' '.join(text_arr) + ' '

    def insert_original_oov(self, text):

        text_arr = text.split()
        for ind, wrd in enumerate(text_arr):
            if wrd == 'x':
                text_arr[ind] = self.current_oov_queue.get()

        return ' '.join(text_arr)

    def fst_stringcompile(self, text):
        compiler = fst.Compiler()
        state_counter = 0
        for c in text:
            uni = self.utf8_symbols.find(c)
            if uni == -1:
                conv = '0x%04x' % ord(c)
                uni = self.utf8_symbols.find(conv)
            from_state = state_counter
            to_state = state_counter + 1
            entry = "{} {} {} {}\n".format(from_state, to_state, uni, uni)
            compiler.write(entry)
            state_counter += 1

        compiler.write("{}\n\n".format(state_counter))

        input_fst = compiler.compile()
        # need to convert to pynini-fst for the combination with the grammar fst
        pynini_fst = pn.Fst.from_pywrapfst(input_fst)

        return pynini_fst

    def get_all_expansions(self, input_fst):
        all_expansions = pn.compose(input_fst, self.exp_grammar)
        all_expansions.set_output_symbols(self.word_symbols)
        all_expansions.optimize()
        all_expansions.project(True)
        all_expansions.arcsort()

        return all_expansions

    def get_best_expansion(self, expansions):
        print("combining expansions and LM ...")
        best_exp = pn.intersect(expansions, self.LM)
        print("optimizing intersection ...")
        best_exp.optimize()
        #best_exp.draw('best.dot')
        shortest_path = pn.shortestpath(best_exp, nshortest=1).optimize()
        #shortest_path.draw('shortest.dot')
        return shortest_path

    def normalize(self, text):
        clean_text = self.clean(text)
        input_fst = self.fst_stringcompile(clean_text)
        all_expansions = self.get_all_expansions(input_fst)
        #all_expansions.draw('all_exp.dot')
        best_expansion = self.get_best_expansion(all_expansions)
        normalized_text = best_expansion.stringify(token_type=self.word_symbols)
        normalized_text = self.insert_original_oov(normalized_text)
        return normalized_text


def main():
    input_text = sys.argv[1]
    #input_text = 'þessir 2 kennarar'
    exp = Expander('expander.conf')
    normalized = exp.normalize(input_text + ' ')

    print("Input: " + input_text)
    print("Normalized: " + normalized)


if __name__ == '__main__':
    main()