#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright: Reykjavik University
Author: Anna Björk Nikulásdóttir
License: Apache 2.0

Creates a language model from a given corpus. Per default uses all the words in the corpus, but you can also
pass the word-symbol file to use as argument.
Remember if you are preparing text normalization that the word-symbol table used to create the language model
has to be the same table used for the grammar and expansion algorithm.

Be sure to have OpenGRM installed: http://www.openfst.org/twiki/bin/view/GRM/NGramLibrary
"""
import os
import argparse
import logging
import time
import subprocess


def create_symbol_table(corpus):
    sym_table = os.path.splitext(corpus)[0] + '_words.sym'
    cmd = "ngramsymbols < {} > {}".format(corpus, sym_table)
    subprocess.call(cmd, shell=True)
    return sym_table


def make_ngram_lm(corpus, word_syms=None, order=3):
    corpus_basename = os.path.splitext(corpus)[0]
    start = time.time()
    if word_syms is None:
        logging.info("Creating word-symbol table ...")
        word_syms = create_symbol_table(corpus_basename)

    logging.info(" Compiling corpus ...")
    cmd = "farcompilestrings -symbols={} -keep_symbols=1 {} > {}.far".format(word_syms, corpus, corpus_basename)
    subprocess.call(cmd, shell=True)
    logging.info(" Creating n-gram model ...")
    cmd = "ngramcount -order={} {}.far > {}.cnt".format(order, corpus_basename, corpus_basename)
    subprocess.call(cmd, shell=True)
    cmd = "ngrammake {}.cnt > {}.mod".format(corpus_basename, corpus_basename)
    subprocess.call(cmd, shell=True)
    cmd = "ngramprint --ARPA {}.mod > {}.arpa".format(corpus_basename, corpus_basename)
    subprocess.call(cmd, shell=True)
    cmd = "ngramread --ARPA {}.arpa > {}.fst".format(corpus_basename, corpus_basename)
    subprocess.call(cmd, shell=True)
    end = time.time()
    logging.info(" Language model created in: '{}.fst'".format(corpus_basename))
    logging.info(" LM training took around {} seconds. Info:".format(int(round(end - start))))
    cmd = "ngraminfo {}.fst".format(corpus_basename)
    subprocess.call(cmd, shell=True)


def arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("corpusfile", type=str, help='the corpus to create the language model from')
    parser.add_argument("--word_symbol", type=str, default=None,
                        help='word-symbol table for the language model')
    parser.add_argument("--order", type=int, default=3,
                        help='size of n-gram to use for model training')

    return parser.parse_args()


def main():
    args = arguments()
    corpus = args.corpusfile
    word_sym = args.word_symbol
    ngram_order = args.order
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.info(("\nCreating a {}-gram language model for '{}' using '{}'\n").format(ngram_order, corpus, word_sym))

    make_ngram_lm(corpus, word_syms=word_sym, order=ngram_order)


if __name__=='__main__':
    main()