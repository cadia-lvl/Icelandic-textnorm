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


"""

import os
import configparser
from timeit import default_timer as timer
import pynini as pn
import nlp
from fst_parser import FSTParser
from tokenizer import Tokenizer
from classifier import Classifier
from verbalizer import Verbalizer
from utterance_structure.utt_coll import UtteranceCollection
from utterance_structure.utt_coll import Utterance
from utterance_structure.utt_coll import TokenType


class Normalizer:

    def __init__(self, configfile='normalizer.conf', working_dir=None, verbalize=True, test_mode=False, tag_mode=False):

        #TODO: print out info on used language model/grammar mode/test mode
        if working_dir:
            current_dir = working_dir
        else:
            current_dir = os.getcwd() + '/'

        config = configparser.ConfigParser()
        config.read(current_dir + configfile)

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
        self.verbalize = verbalize
        if verbalize:
            self.verbalizer = Verbalizer(verbalizer_grammar_file, lm_file, self.utf8_symbols, word_symbols)
        self.utterance_collection = None
        self.test_mode = test_mode
        self.tag_mode = tag_mode


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
            print("processing '" + sent + "' ...")
            self.utterance_collection.add_utterance(Utterance(sent))
        for utt in self.utterance_collection.collection:
            self._normalize_utterance(utt)
            if self.verbalize and not self.test_mode:
                normalized_text.append(utt.normalized_sentence)
            elif self.test_mode:
                normalized_text.append(utt.get_test_output())
            else:
                normalized_text.append(utt.classified)

        return '\n'.join(normalized_text)


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
        classified_fst = self._classify(utt)
        if not utt.classified:
            return
        if self.verbalize:
            self._verbalize(classified_fst, utt)

        if utt.reclassify:
            # Some token(s) could not be normalized and where split up into single character tokens
            # during the verbalizing process. Do a re-classification and verbalization.
            utt.reclassify = False
            utt.tokenized_string = self._retokenize(utt)
            utt.ling_structure.tokens = []
            classified_fst = self._classify(utt)
            if self.verbalize:
                self._verbalize(classified_fst, utt)

        if self._normalization_failed(utt):
            # TODO: logging
            print('Normalization failed for "' + utt.original_sentence + '"')


    def _classify(self, utt):

        classified_fst, stringified = self.classifier.classify(utt.tokenized_string)
        utt.classified = stringified
        return classified_fst

    def _verbalize(self, classified_fst, utt):
        parser = FSTParser(self.utf8_symbols)
        parser.parse_tokens_from_fst(classified_fst, utt)
        if self.tag_mode:
            self._tag_utterance(utt)
        self.verbalizer.verbalize(utt)


    def _tag_utterance(self, utt):
        #tagged = nlp.tag_sentence(utt.original_sentence)
        token_arr = []
        for tok in utt.ling_structure.tokens:
            token_arr.append(tok.word)
        tokens = '\n'.join(token_arr)
        tagged = nlp.tag_sentence(tokens)
        print(tagged)
        tagged_arr = tagged.split()
        tag_ind = 0
        for ind, tok in enumerate(utt.ling_structure.tokens):
            if tok.token_type != TokenType.SEMIOTIC_CLASS:
                tagged_token = tagged_arr[tag_ind]
                while tagged_token[:tagged_token.index('_')].lower() != tok.word.lower():
                    tag_ind += 1
                    tagged_token = tagged_arr[tag_ind]
                tok.word = tagged_arr[tag_ind]



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
    import sys
    start = timer()
    #input_text = "Afkoma ársins 2017 var góð."
    input_text_x = "Afkoma ársins 2017 var góð. Hagnaður fyrir óinnleysta fjármagnsliði hefur aldrei verið meiri. " \
                 "Tekjur voru meiri en nokkru sinni fyrr og sett voru met í orkuvinnslu og -sölu á árinu. " \
                 "Selt magn var 14,3 twst og jókst um 5,1% milli ára. " \
                 "DNA-rannsóknir eða rannsóknir á kjarnasýrunum."


    inp = 'test_from_training_data_visir201303.txt'
    output = '../evaluation/eval_results_final/training_test_MIXED.txt'
    input_text = open(inp).read().splitlines()
    norm = Normalizer(test_mode=True, tag_mode=False)
    #inp = ' Bryndís Rún Hansen varð annar Íslendingurinn á HM í 25 m laug í Kanada til að komast í undanúrslit í sinni grein en það gerði hún í 50 m flugsundi nú síðdegis .'
    #inp = 'Um 2 prósent nefna og 3 prósent'
    #normalized = norm.normalize(inp)
    #print(normalized)
    #exit()
    all_normalized = []
    for line in input_text:
        normalized = norm.normalize(line)
        #whole lines, original + normalization
        #all_normalized.append(line + '\t' + normalized)
        #test output, token-by-token
        all_normalized.append(normalized)
        #if len(all_normalized)%500 == 0:
        #    with open(output, 'a') as f:
        #        for sent in all_normalized:
        #            if sent != "I'm normalized":
        #                f.write(sent + '\n')
        #    all_normalized = []

    end = timer()
    print('Total duration: ' + str(end - start))

    with open(output, 'w') as f:
        for norm in all_normalized:
            if norm != "I'm normalized":
                f.write(norm + '\n')

    #norm.print_normalized_text()

    #with open("utterance.json") as read_file:
    #    utt_in = read_file.read()
    #    utt_obj = jsonpickle.decode(utt_in)
    #    print("Decoded:")
    #    print(utt_obj.print_classified())
    #    print(utt_obj.original_sentence)


if __name__ == '__main__':
    main()