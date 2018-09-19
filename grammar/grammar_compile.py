#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compile a thrax grammar and the utf8 to word FST. The utf8 to word FST has to be compiled from the same
word symbol table that is used for language model creation, if the grammar is going to be used with
that language model.

"""

import sys
import pynini as pn


def main():
    grammarfile = sys.argv[1]
    utf8_word_fst_file = sys.argv[2]
    output_fst = sys.argv[3]

    inp_grammar = pn.Fst.read(grammarfile)
    utf8_word_fst = pn.Fst.read(utf8_word_fst_file)
    grammar = pn.compose(inp_grammar, utf8_word_fst)
    grammar.rmepsilon()
    mapped = pn.arcmap(grammar, map_type="arc_sum")
    mapped.arcsort()

    mapped.write(output_fst)


if __name__=='__main__':
    main()