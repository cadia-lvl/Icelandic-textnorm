#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Contains tokenizer methods from the nltk.tokenize library.

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
            # ABN: added to handle non-pronunceable dashes, like Súes-skurðinn'
            # keep dashes after digits and ordinals, and SNAV (directions). Add 'a-ö'?
            (re.compile(r'([^\.\d[A-ZÞÆÖÁÉÍÓÚÝÐ])([-])'), r'\1 '),
            (re.compile(r'([:,])$'), r' \1 '),
            (re.compile(r'\.\.\.'), r' ... '),
            (re.compile(r'[;#$&]'), r' \g<0> '),
            # Handles the final period.
            # #ABN: changed this to deal with ordinals at the end of sentence: [^\.] -> [^\.\d], don't detach '.' after a digit. (Might be too general)
            (re.compile(r'([^\.\d])(\.)([\]\)}>"\']*)\s*$'), r'\1 \2\3 '),
            (re.compile(r'[?!]'), r' \g<0> '),

            (re.compile(r"([^'])' "), r"\1 ' "),
        ]

    def tokenize_sentence(self, text):
        sentence_list = sent_tokenize(text)
        return sentence_list

    def tokenize_words(self, sentence):
        word_list = self.tokenizer.tokenize(sentence)

        return word_list


def main():
    tok = Tokenizer()

    s_list = tok.tokenize_sentence("Tíu árum eftir hrun vita Björn Arnarson og Halla Sigrún Gylfadóttir, hjón með tvö "
                                   "börn í hálfkláruðu húsi, loksins hvað þau skulda Arion banka. Af þessum 240 atriðum "
                                   "eru yfir 150 íslensk bönd en hátíðin fer fram 7.-10. nóvember. Draumur þeirra að "
                                   "byggja fallegt hús við Elliðavatn í Kópavogi varð að martröð við fall bankanna í "
                                   "október 2008. Björn og Halla voru á meðal þeirra sem sögðu sögu sína í "
                                   "heimildarmyndinni Nýja Ísland sem sýnd var á Stöð 2 í vikunni.")

    w_list = tok.tokenize_words('í Súes-skurðinn 3-5 á N- og A-landi V-til fyrir ab-mjólk handa A-landsliðinu þann 5. des.')

    print(' '.join(w_list))

    for elem in w_list:
        print(elem)

if __name__=='__main__':
    main()