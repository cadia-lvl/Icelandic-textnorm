#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jsonpickle
from enum import Enum
import utterance_structure.semiotic_classes

class UtteranceCollection:

    def __init__(self):
        self.collection = []

    def add_utterance(self, utt):
        if not isinstance(utt, Utterance):
            raise TypeError("'" + str(utt) + "' is " + str(type(utt)) +
                            "\nYou can only add objects of type 'Utterance' to the utterance collection!")

        self.collection.append(utt)


class Utterance(object):

    def __init__(self, inp):
        self.original_sentence = inp
        self.normalized_sentence = "I'm normalized" # or same as original at initialization time?
        self.ling_structure = LinguisticStructure(inp)
        self.tokenized = []
        self.tokenized_string = ""
        self.classified = ""

    def to_jsonpickle(self, filename):
        json_enc = jsonpickle.encode(self)
        with open(filename, 'w') as f:
            f.write(json_enc)

    def print_classified(self):
        print(self.classified)

    def print_tokenized(self):
        print(' '.join(self.tokenized))

    def print_original(self):
        print(self.original_sentence)

    def print_normalized(self):
        print(self.normalized_sentence)

    def print(self):
        ling_struct = self.ling_structure
        print(self.original_sentence)
        print(self.classified)
        for tok in ling_struct.tokens:
            print('')
            tok.print()


class LinguisticStructure(object):

    def __init__(self, inp):
        self.ls_id = 0
        self.input_sentence = inp
        self.tokens = []
        self.words = []


class TokenType(str, Enum):
    WORD = 'word'
    SEMIOTIC_CLASS = 'sem_class'
    PUNCT = 'punct'
    NEEDS_VERBALIZATION = 'needs_verbal'

class PauseLength(str, Enum):
    PAUSE_NONE = 'none'
    PAUSE_SHORT = 'short'
    PAUSE_MEDIUM = 'medium'
    PAUSE_LONG = 'long'


class Token(object):

    def __init__(self):
        self.token_type = None
        self.semiotic_class = None
        self.name = ''
        self.word = ''
        self.wordid = ''
        self.pause_length = PauseLength.PAUSE_NONE
        self.phrase_break = False

        self.start_index = 0
        self.end_index = 0

    def set_token_type(self, token_type):
        self.token_type = token_type

    def set_semiotic_class(self, sem_class):
        self.semiotic_class = sem_class

    def set_name(self, name):
        self.name = name

    def set_word(self, wrd):
        self.word = wrd

    def set_wordid(self, wid):
        self.wordid = wid

    def set_pause_length(self, pl):
        self.pause_length = pl

    def set_phrase_break(self, pb):
        self.phrase_break = pb

    def has_name(self):
        if self.name:
            return True
        return False

    def set_value(self, tuple, sem_class_label):
        if 'name:' in tuple:
            self.name = tuple['name:']
            self.word = self.name.lower()

        if 'pause_length:' in tuple:
            val = tuple['pause_length:']
            if val == 'PAUSE_SHORT':
                self.pause_length = PauseLength.PAUSE_SHORT
            elif val == 'PAUSE_MEDIUM':
                self.pause_length = PauseLength.PAUSE_MEDIUM
            elif val == 'PAUSE_LONG':
                self.pause_length = PauseLength.PAUSE_LONG

        if 'phrase_break:' in tuple:
            if tuple['phrase_break:'] == 'true':
                self.phrase_break = True

        if 'type:' in tuple:
            if tuple['type:'] == 'PUNCT':
                self.token_type = TokenType.PUNCT

        if sem_class_label:
            self.semiotic_class = self.get_semiotic_class(sem_class_label, tuple)
            self.token_type = TokenType.SEMIOTIC_CLASS



    def get_semiotic_class(self, label, content):

        if label == 'cardinal':
            return utterance_structure.semiotic_classes.Cardinal(content['integer:'])
        if label == 'ordinal':
            return utterance_structure.semiotic_classes.Ordinal(content['integer:'])

    def print(self):
        print('TokenType: ' + str(self.token_type))
        print('Semiotic class: ' + str(self.semiotic_class))
        print('Name: ' + self.name)
        print('Word: ' + self.word)
        print('Pause length: ' + str(self.pause_length))
        print('Phrase break: ' + str(self.phrase_break))






