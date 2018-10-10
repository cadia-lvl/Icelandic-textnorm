#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright: Reykjavik University
Author: Anna Björk Nikulásdóttir
License: Apache 2.0

The LVL text normalizer follows the ideas of Sparrowhawk (cit.) for a two step text normalization:

    1) tokenizing and classifying
    2) verbalizing

"""

from tokenizer import Tokenizer
from utt_coll import UtteranceCollection
from utt_coll import Utterance

class Normalizer:

    def __init__(self, input_text):
        self.original_text = input_text
        self.utterance_collection = UtteranceCollection()


    def normalize(self):
        tok = Tokenizer()
        sentence_list = tok.tokenize_sentence(self.original_text)
        for sent in sentence_list:
            self.utterance_collection.add_utterance(Utterance(sent))


    def print_normalized_text(self):
        for utt in self.utterance_collection.collection:
            utt.print()

def main():
    input_text = "Tíu árum eftir hrun vita Björn Arnarson og Halla Sigrún Gylfadóttir, hjón með tvö börn í hálfkláruðu " \
                 "húsi, loksins hvað þau skulda Arion banka. Af þessum 240 atriðum eru yfir 150 íslensk bönd en " \
                 "hátíðin fer fram 7.-10. nóvember. Draumur þeirra að byggja fallegt hús við Elliðavatn í Kópavogi varð " \
                 "að martröð við fall bankanna í október 2008. Björn og Halla voru á meðal þeirra sem sögðu sögu sína í " \
                 "heimildarmyndinni Nýja Ísland sem sýnd var á Stöð 2 í vikunni."

    norm = Normalizer(input_text)
    norm.normalize()
    norm.print_normalized_text()


if __name__ == '__main__':
    main()