#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


    def print(self):
        print(self.original_sentence)
