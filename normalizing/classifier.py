#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classify an utterance according to a Thrax classify grammar


"""
import pynini as pn
import pywrapfst as fst


class Classifier:

    def __init__(self, path_to_grammar='/Users/anna/sparrowhawk/sparrowhawk/documentation/grammars/ice/classify/TOKENIZE_AND_CLASSIFY'):
        self.thrax_grammar = pn.Fst.read(path_to_grammar)
        self.thrax_grammar.arcsort()
        self.utf8_symbols = pn.SymbolTable.read_text('data/utf8.syms')

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
        pynini_fst = pn.Fst.from_pywrapfst(input_fst)

        return pynini_fst

    def classify(self, text):
        inp_fst = self.fst_stringcompile(text)
        all_fst = pn.compose(inp_fst, self.thrax_grammar)
        shortest_path = pn.shortestpath(all_fst).optimize()

        classified = shortest_path.stringify(token_type=self.utf8_symbols)
        classified = classified.replace(' ', '')
        classified = classified.replace('0x0020', ' ')
        return shortest_path, classified


def main():
    classifier = Classifier()

    print(classifier.classify("af þessum 240 atriðum"))


if __name__ == '__main__':
    main()
