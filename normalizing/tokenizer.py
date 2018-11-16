#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Contains tokenizer methods from the nltk.tokenize library.

TODO: do we need adaption to Icelandic? Vilhjálmur's tokenizer?
If this class does not get extended in the course of the project, move these methods to a util module
"""

from nltk.tokenize import sent_tokenize
from nltk.tokenize import TreebankWordTokenizer

import re
class Tokenizer:

    def __init__(self):
        self.tokenizer = TreebankWordTokenizer()
        # remove % and @ from the4th list as compared to original PUNCTUATION:
        self.tokenizer.PUNCTUATION = [
            (re.compile(r'([:,])([^\d])'), r' \1 \2'),
            (re.compile(r'([:,])$'), r' \1 '),
            (re.compile(r'\.\.\.'), r' ... '),
            (re.compile(r'[;#$&]'), r' \g<0> '),
            (re.compile(r'([^\.])(\.)([\]\)}>"\']*)\s*$'), r'\1 \2\3 '),  # Handles the final period. #ABN: change this to deal with ordinals at the end of sentence
            (re.compile(r'[?!]'), r' \g<0> '),

            (re.compile(r"([^'])' "), r"\1 ' "),
        ]

    def tokenize_sentence(self, text):
        sentence_list = sent_tokenize(text)
        return sentence_list

    def tokenize_words(self, sentence):
        # drullumix - need to fix this within the tokenizer
        # the tokenizer always cuts the last dot of the sentence, even if it is a date like '14.10.'
        # don't want that.
        remove_last = False
        if re.match('.*\d{1,2}\.\d{1,2}\.$', sentence):
            sentence = sentence + ' auka'
            remove_last = True
        word_list = self.tokenizer.tokenize(sentence)
        if remove_last:
            word_list = word_list[:-1]
        return word_list


def main():
    tok = Tokenizer()

    s_list = tok.tokenize_sentence("Tíu árum eftir hrun vita Björn Arnarson og Halla Sigrún Gylfadóttir, hjón með tvö "
                                   "börn í hálfkláruðu húsi, loksins hvað þau skulda Arion banka. Af þessum 240 atriðum "
                                   "eru yfir 150 íslensk bönd en hátíðin fer fram 7.-10. nóvember. Draumur þeirra að "
                                   "byggja fallegt hús við Elliðavatn í Kópavogi varð að martröð við fall bankanna í "
                                   "október 2008. Björn og Halla voru á meðal þeirra sem sögðu sögu sína í "
                                   "heimildarmyndinni Nýja Ísland sem sýnd var á Stöð 2 í vikunni.")

    w_list = tok.tokenize_words(s_list[1])

    print(' '.join(w_list))

    for elem in w_list:
        print(elem)

if __name__=='__main__':
    main()