#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum

class UtteranceCollection:

    def __init__(self):
        self.collection = []

    def add_utterance(self, utt):
        if not isinstance(utt, Utterance):
            raise TypeError("'" + str(utt) + "' is " + str(type(utt)) +
                            "\nYou can only add objects of type 'Utterance' to the utterance collection!")

        self.collection.append(utt)


class Utterance:

    def __init__(self, inp):
        self.original_sentence = inp
        self.ling_structure = LinguisticStructure(inp)
        self.tokenized = []
        self.tokenized_string = ""
        self.classified = ""


    def print_classified(self):
        print(self.classified)

    def print_tokenized(self):
        print(' '.join(self.tokenized))

    def print_original(self):
        print(self.original_sentence)

    def print(self):
        ling_struct = self.ling_structure
        print(self.original_sentence)
        print(self.classified)
        for tok in ling_struct.tokens:
            print('')
            tok.print()


class LinguisticStructure:

    def __init__(self, inp):
        self.ls_id = 0
        self.input_sentence = inp
        self.tokens = []
        self.words = []


class TokenType(Enum):
    WORD = 1
    SEMIOTIC_CLASS = 2
    PUNCT = 3
    NEEDS_VERBALIZATION = 4

class PauseLength(Enum):
    PAUSE_NONE = 0
    PAUSE_SHORT = 1
    PAUSE_MEDIUM = 2
    PAUSE_LONG = 3


class Token:

    def __init__(self):
        self.token_type = None
        #self.verify(token_type, sem_class, word)
        self.semiotic_class = None
        self.name = ''
        self.word = ''
        self.wordid = ''
        self.pause_length = PauseLength.PAUSE_NONE
        self.phrase_break = False

        self.start_index = 0
        self.end_index = 0

    def verify(self, sem_class, word):
        if self.token_type == TokenType.SEMIOTIC_CLASS and sem_class is None:
            raise ValueError('TokenType SEMIOTIC_CLASS has to have an initialized semiotic class object!')
        if self.token_type == TokenType.WORD and word is None:
            raise ValueError('TokenType WORD has to have a word string!')

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

    def set_value(self, tuple):
        if 'name:' in tuple:
            self.name = tuple['name:']
            self.word = self.name.lower()

    def print(self):
        print('TokenType: ' + str(self.token_type))
        print('Semiotic class: ' + str(self.semiotic_class))
        print('Name: ' + self.name)
        print('Word: ' + self.word)
        print('Pause length: ' + str(self.pause_length))
        print('Phrase break: ' + str(self.phrase_break))





