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
#import jsonpickle
#import json
import os
import configparser
import pynini as pn
from fst_parser import FSTParser
from tokenizer import Tokenizer
from classifier import Classifier
from verbalizer import Verbalizer
from utterance_structure.utt_coll import UtteranceCollection
from utterance_structure.utt_coll import Utterance

class Normalizer:

    def __init__(self, configfile='normalizer.conf', working_dir=None):

        if working_dir:
            current_dir = working_dir
        else:
            current_dir = os.getcwd() + '/'

        config = configparser.ConfigParser()
        config.read(working_dir + configfile)
        data_dir = current_dir + config['DATA_DIR']['data']
        utf8_symfile = data_dir + config['symbol tables']['utf8']
        word_symfile = data_dir + config['symbol tables']['word-symbol']
        lm_file = data_dir + config['models']['language model']
        thrax_dir = data_dir + config['thrax']['thrax']
        path_to_classifier = thrax_dir + config['thrax grammars']['classifier grammar']
        verbalizer_grammar_file = thrax_dir + config['thrax grammars']['verbalizer grammar']

        self.utf8_symbols = pn.SymbolTable.read_text(utf8_symfile)
        word_symbols = pn.SymbolTable.read_text(word_symfile)

        self.tok = Tokenizer()
        self.classifier = Classifier(path_to_classifier, self.utf8_symbols)
        self.verbalizer = Verbalizer(verbalizer_grammar_file, lm_file, self.utf8_symbols, word_symbols)


    def normalize_utterance(self, utt):

        utt.tokenized = self.tok.tokenize_words(utt.original_sentence)
        utt.tokenized_string = ' '.join(utt.tokenized)
        classified_fst, stringified = self.classifier.classify(utt.tokenized_string)
        utt.classified = stringified
        parser = FSTParser(classified_fst, self.utf8_symbols)
        parser.parse_tokens_from_fst(utt)
        #utt.to_jsonpickle(utt.original_sentence + '_utt.json')
        self.verbalizer.verbalize(utt)


    def normalize(self, text):
        self.utterance_collection = UtteranceCollection()
        normalized_text = []
        sentence_list = self.tok.tokenize_sentence(text)
        for sent in sentence_list:
            self.utterance_collection.add_utterance(Utterance(sent))
        for utt in self.utterance_collection.collection:
            self.normalize_utterance(utt)
            normalized_text.append(utt.normalized_sentence)

        return ' '.join(normalized_text)

    def print_normalized_text(self):
        for utt in self.utterance_collection.collection:
            utt.print_classified()
            utt.print_normalized()

def main():

    input_text = "þessi 3 börn"
    input_text_x = "Tíu árum eftir hrun vita Björn Arnarson og Halla Sigrún Gylfadóttir, hjón með tvö börn í hálfkláruðu " \
                 "húsi, loksins hvað þau skulda Arion banka. Af þessum 240 atriðum eru yfir 150 íslensk bönd en " \
                 "hátíðin fer fram 7.-10. nóvember. Draumur þeirra að byggja fallegt hús við Elliðavatn í Kópavogi varð " \
                 "að martröð við fall bankanna í október 2008. Björn og Halla voru á meðal þeirra sem sögðu sögu sína í " \
                 "heimildarmyndinni Nýja Ísland sem sýnd var á Stöð 2 í vikunni."

    norm = Normalizer()
    norm.normalize(input_text)

    norm.print_normalized_text()
    """
    with open("utterance.json") as read_file:
        utt_in = read_file.read()
        utt_obj = jsonpickle.decode(utt_in)
        print("Decoded:")
        print(utt_obj.print_classified())
        print(utt_obj.original_sentence)
    """

if __name__ == '__main__':
    main()