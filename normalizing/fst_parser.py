#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pynini as pn
import pywrapfst as fst
from classifier import Classifier
from utterance_structure.utt_coll import Token, TokenType

SPACE = 32
QUOTES = 34
COLON = 58
CURLY_OPEN = 123
CURLY_CLOSE = 125

SEPARATORS = [SPACE, CURLY_OPEN, CURLY_CLOSE]

SUBSTRUCTURE = ['cardinal']


class FSTParser:

    def __init__(self, classifier_fst):
        self.fst = classifier_fst
        self.state = self.fst.start()
        self.last_state = self.fst.start()
        self.inp_label = 0
        self.out_label = 0
        self.token_start = 0
        self.last_token_end = 0
        self.num_states = classifier_fst.num_states()
        classifier = Classifier()
        self.utf8symbols = classifier.utf8_symbols

        self.token_name = '' # does this belong here?

    def parse_tokens_from_fst(self, utt):
        """
        if self.state < self.fst.start or self.state >= self.fst.num_states():
            raise ValueError('Invalid state: {}'.format(self.state))
        """
        while self.state < self.fst.num_states() - 1:
            label = self.consume_label()
            if label != 'tokens':
                #print('Error - label is ' + label + ' and not "tokens"')
                #return False
                print('not tokens!')
                break
            self.next_state()
            token = Token()
            self.parse_message(token)
            self.update_utterance(utt, token, False)

       # utt.print()


    def consume_label(self):
        label_arr = []
        while self.next_state():
            if (self.out_label == SPACE and not label_arr) or self.out_label == 0:
                continue
            elif not self.is_separator(self.out_label):
                label_arr.append(self.utf8symbols.find(self.out_label).decode('utf-8'))
            elif self.out_label == CURLY_CLOSE and not label_arr:
                label_arr.append(self.utf8symbols.find(self.out_label).decode('utf-8'))
                break
            else:
                if self.out_label != COLON and self.out_label != SPACE:
                    self.prev_state()
                break

        self.consume_whitespace()
        return ''.join(label_arr)

    #TODO: deal with this: tokens { name: "." pause_length: PAUSE_LONG phrase_break: true type: PUNCT }
    # change name when the code is ready
    def parse_message(self, tok, sem_class_label=None):
        field_order = []
        while True:
            label = self.consume_label()
            if label == '}':
                return
            field_order.append(label)
            if label in SUBSTRUCTURE:
                self.next_state()
                self.parse_message(tok, sem_class_label=label)

            # add: going into sub-field, like cardinal { integer: ... }}? Parse that token here
            # else we have a value: (label like cardinal does not have a terminal value)
            else:
                value = self.parse_field_value()
                tok.set_value({label: value}, sem_class_label)


        self.consume_whitespace()

    def parse_field_value(self):
        value_arr = []
        while self.next_state():
            if self.out_label == QUOTES:
                value_arr = self.parse_quoted_field_value(value_arr)
            elif self.out_label == SPACE:
                return ''.join(value_arr)
            elif self.out_label == CURLY_CLOSE:
                self.prev_state() # unconsume the curly brace
                return ''.join(value_arr)
            elif self.out_label:
                value_arr.append(self.utf8symbols.find(self.out_label).decode('utf-8'))


    def parse_quoted_field_value(self, arr):

        while self.next_state():
            if self.out_label != QUOTES:
                arr.append(self.utf8symbols.find(self.out_label).decode('utf-8'))
            else:
                return arr

    def next_state(self):
        arc_it = self.fst.arcs(self.state)
        if arc_it.done():
            return False

        self.inp_label = arc_it.value().ilabel
        self.out_label = arc_it.value().olabel

        if self.inp_label != 0:
            # Don't aggregate leading whitespace against a token
            if self.inp_label == SPACE and not self.token_name:
                self.token_start += 1
            else:
                self.token_name + self.utf8symbols.find(self.inp_label).decode('utf-8')

        self.last_state = self.state
        self.state = arc_it.value().nextstate

        return True

    def prev_state(self):
        self.state = self.last_state

        # Undo any input aggregation we might have done
        if self.inp_label:
            if self.inp_label == SPACE and not self.token_name:
                self.token_start -= 1
            elif self.token_name:
                self.token_name = self.token_name[:-1]


    def consume_whitespace(self):
        while self.next_state():
            if self.out_label != SPACE and self.out_label != 0:
                self.prev_state()
                break


    def update_utterance(self, utt, token, set_semiotic_class):

        token_end = self.token_start + len(token.name)
        token.start_index = self.token_start
        self.last_token_end = token_end - 1
        token.end_index = self.last_token_end

        if token.has_name():
            token.set_wordid(token.name)
            token.set_token_type(TokenType.WORD)
        else:
            token.set_name(self.token_name)
            if set_semiotic_class:
                token.set_token_type(TokenType.SEMIOTIC_CLASS)

        utt.ling_structure.tokens.append(token)

        self.token_start = token_end
        self.last_token_name = self.token_name
        self.token_name = ''

    def is_separator(self, elem):
        if elem in SEPARATORS:
            return True
        return False