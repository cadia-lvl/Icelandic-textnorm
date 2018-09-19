#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Creates the utf8-to-word symbol table needed to be able to combine the grammar and the language model.

The grammar is utf8-symbol based, but the language model is word-symbol based, we compose the output fst of this
script with a grammar, which is then ready to be composed with a word-symbol based FST created from input to
normalize as well as with the language model, that also uses the same word-symbol table.

Input files:

- a word-symbol table (the same as the language model and input text FSTs use), make sure the first entry is:

  <eps> 0

- utf8-symbol table (complete mappings of utf8 symbols to unicode values)

Output:

- FST mapping from utf8 unicode repr. to the symbols in the word-symbol table

Example ('3' is the symbol for 'aftur' in the word-symbol table):

    97:0 -> 102:0 -> 116:3 -> 117:0 -> 114:0 -> 32:0

    ('a':0 -> 'f':0 -> 't':'aftur' -> 'u':0 -> 'r':0 -> ' ':0)

"""

import sys
import os
import pynini as pn
import pywrapfst as fst

SPACE = '0x%04x' % ord(' ')


def convert_words2utf8(sym_table_file):
    """
    sym_table:
    ...
    baki 868
    bakinu 869
    ...

    words2utf8:
    ...
    baki b a k i 0x0020
    bakinu b a k i n u 0x0020
    ...

    :param sym_table:
    :return: words2utf8
    """
    sym_table = open(sym_table_file).readlines()
    words2utf8 = []
    for line in sym_table:
        word, sym = line.split()
        if word == '<eps>':
            continue
        entry = word + ' ' + ' '.join(word) + ' ' + SPACE
        words2utf8.append(entry)

    return words2utf8


def make_lexicon_fst(inp_lexicon, outp_lexicon):
    """
    Creates a lexicon FST that transduces phones to words, and may allow optional silence.

    inp_lexicon:
    ...
    Adam A d a m 0x0020
    ...

    output_lexicon:
    ...
    0	63	A	Adam
    63	64	d	<eps>
    64	65	a	<eps>
    65	66	m	<eps>
    66	0	0x0020	<eps>
    ...

    :param inp_lexicon:
    :param outp_lexicon:
    :return:
    """
    cmd = 'perl make_lexicon_fst.pl {} > {}'.format(inp_lexicon, outp_lexicon)
    os.system(cmd)


def write_list(list2write, filename):
    with open(filename, 'w') as f:
        for e in list2write:
            f.write(e + '\n')


def compile_fst(fst_list, inp_sym, out_sym):
    """
    Compile the fst-lexicon with utf8 symbols as input symbols and words as output symbols
    :param fst_list:
    :param inp_sym:
    :param out_sym:
    :return: the compiled fst
    """

    compiler = fst.Compiler()
    for line in fst_list:
        if len(line.split('\t')) != 4:
            break
        from_state, to_state, inp, outp = line.split('\t')
        inp_int = inp_sym.find(inp)
        outp_int = out_sym.find(outp.strip())
        if inp_int == -1 or outp_int == -1:
            print("symbol {} and/or {} not found!".format(inp, outp))
            continue
        entry = "{} {} {} {}\n".format(from_state, to_state, inp_int, outp_int)
        compiler.write(entry)

    compiler.write("{}\n\n".format(0))

    compiled_fst = compiler.compile()
    # need to convert to pynini-fst for the combination with the grammar fst
    pynini_fst = pn.Fst.from_pywrapfst(compiled_fst)

    return pynini_fst


def compile_utf8_to_words(wordsymbolfile, utf8symbolfile, lex_fst_file):

    utf8syms = pn.SymbolTable.read_text(utf8symbolfile)
    words2syms = pn.SymbolTable.read_text(wordsymbolfile)

    compiled = compile_fst(open(lex_fst_file).readlines(), utf8syms, words2syms)
    compiled.set_input_symbols(utf8syms)
    compiled.set_output_symbols(words2syms)
    compiled.arcsort()
    compiled.closure()
    compiled.optimize()  # same as fstdeterminizestar | fstminimize ?
    compiled.arcsort()

    lex_filename = wordsymbolfile.split('/')
    lex_basename = os.path.splitext(lex_filename[-1])[0]
    compiled.write('utf8_to_words_{}.fst'.format(lex_basename))


def main():

    wordsymbolfile = sys.argv[1]
    utf8symbolfile = sys.argv[2]

    words2utf8 = convert_words2utf8(wordsymbolfile)
    write_list(words2utf8, 'words2utf8.tmp')
    make_lexicon_fst('words2utf8.tmp', 'lexicon_fst.txt')

    compile_utf8_to_words(wordsymbolfile, utf8symbolfile, 'lexicon_fst.txt')


if __name__=='__main__':
    main()