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


class Token:

    def __init__(self, token_type, sem_class=None, word=None):
        self.token_type = token_type
        self.verify(token_type, sem_class, word)
        self.semiotic_class = sem_class
        self.word = word

    def verify(self, sem_class, word):
        if self.token_type == TokenType.SEMIOTIC_CLASS and sem_class is None:
            raise ValueError('TokenType SEMIOTIC_CLASS has to have an initialized semiotic class object!')
        if self.token_type == TokenType.WORD and word is None:
            raise ValueError('TokenType WORD has to have a word string!')



