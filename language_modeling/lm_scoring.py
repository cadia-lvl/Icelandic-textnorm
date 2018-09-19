#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright: Reykjavik University
Author: Anna Björk Nikulásdóttir
License: Apache 2.0

Scores an input sentence or text from file according to a given language model (in .arpa format).

Uses the python module for kenlm language modeling toolkit:

https://github.com/kpu/kenlm

pip install -e kenlm-master

"""

import os
import argparse
import kenlm


def score_input(lm, input):

    print('INPUT: ' + input)
    score = lm.score(input)
    perpl = lm.perplexity(input)
    print('\nSCORE: {}'.format(str(score)))
    print('\nPERPLEXITY: {}'.format(str(perpl)))


def full_score(lm, input):

    print('\nFULL SCORE BY N-GRAMS, SHOWS OOV:\n')
    words = ['<s>'] + input.split() + ['</s>']
    for i, (prob, length, oov) in enumerate(lm.full_scores(input)):
        print('{} {}: {}'.format(prob, length, ' '.join(words[i + 2 - length:i + 2])))
        if oov:
            print('\t"{}" is an OOV'.format(words[i + 1]))

    print("")


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("lm", type=str, help='the language model in arpa format')
    parser.add_argument("input", type=str, help='text to score')

    return parser.parse_args()


def main():
    args = arguments()
    arpa_lm = args.lm
    inp = args.input

    if os.path.isfile(inp):
        text = open(inp).read()
    else:
        text = inp
        
    # create a kenlm language model object
    model = kenlm.LanguageModel(arpa_lm)
    score_input(model, text.lower())
    full_score(model, text.lower())


if __name__=='__main__':
    main()