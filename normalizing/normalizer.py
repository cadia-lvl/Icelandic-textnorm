#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright: Reykjavik University
Author: Anna Björk Nikulásdóttir
License: Apache 2.0
See also LICENSE.txt

The LVL text normalizer 'Haukur' follows the idea of Google's Sparrowhawk/Kestrel for a two step text normalization:

    1) tokenizing and classifying
    2) verbalizing

The normalizer takes a raw text as an input and returns the same text in a normalized form, aimed at being an input
to a TTS system. For setup and configuration see: README.md

References:
    https://github.com/google/sparrowhawk
    Ebden, Peter and Sproat, Richard. 2015. The Kestrel TTS text normalization
    system. Natural Language Engineering, Issue 03, pp 333-353.

TODO: make a classification only procedure possible

"""

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
        self.utterance_collection = None


    def normalize(self, text):
        """
        Normalizes text, i.e. converts all non-standard-words (NSWs) into standard words, readable by a TTS system.

        :param text: a string, one or more sentences
        :return: a normalized version of text where no non-standard-words should be left
        """
        self.utterance_collection = UtteranceCollection()
        normalized_text = []
        sentence_list = self.tok.tokenize_sentence(text)
        for sent in sentence_list:
            self.utterance_collection.add_utterance(Utterance(sent))
        for utt in self.utterance_collection.collection:
            self._normalize_utterance(utt)
            normalized_text.append(utt.normalized_sentence)

        return ' '.join(normalized_text)


    def print_normalized_text(self):
        """
        Prints the classified markup and the final normalized text of the utterance_collection

        :return: None
        """
        for utt in self.utterance_collection.collection:
            utt.print_classified()
            utt.print_normalized()

    #
    #   PRIVATE METHODS
    #

    def _normalize_utterance(self, utt):

        utt.tokenized = self.tok.tokenize_words(utt.original_sentence)
        utt.tokenized_string = ' '.join(utt.tokenized)
        self._classify_and_verbalize(utt)

        if utt.reclassify:
            # Some token(s) could not be normalized and where split up into single character tokens
            # during the verbalizing process. Do a re-classification and verbalization.
            utt.reclassify = False
            utt.tokenized_string = self._retokenize(utt)
            utt.ling_structure.tokens = []
            self._classify_and_verbalize(utt)

        if self._normalization_failed(utt):
            # TODO: logging
            print('Normalization failed for "' + utt.original_sentence + '"')


    def _classify_and_verbalize(self, utt):

        classified_fst, stringified = self.classifier.classify(utt.tokenized_string)
        utt.classified = stringified
        parser = FSTParser(self.utf8_symbols)
        parser.parse_tokens_from_fst(classified_fst, utt)
        self.verbalizer.verbalize(utt)


    def _normalization_failed(self, utt):

        for tok in utt.ling_structure.tokens:
            if tok.verbalization_failed:
                return True

        return False


    def _retokenize(self, utt):

        utt.tokenized = []
        for tok in utt.ling_structure.tokens:
            utt.tokenized.append(tok.name)

        return ' '.join(utt.tokenized)


def main():

    input_text = "þessi 3 börn"

    norm = Normalizer()
    norm.normalize(input_text)

    norm.print_normalized_text()

    #with open("utterance.json") as read_file:
    #    utt_in = read_file.read()
    #    utt_obj = jsonpickle.decode(utt_in)
    #    print("Decoded:")
    #    print(utt_obj.print_classified())
    #    print(utt_obj.original_sentence)


if __name__ == '__main__':
    main()