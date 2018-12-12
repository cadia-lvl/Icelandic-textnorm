#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parses FST representations of classified utterances, collects token information to store with the corresponding
utterance


"""
from utterance_structure.utt_coll import Token, TokenType

EPSILON = 0
SPACE = 32
QUOTES = 34
COLON = 58
CURLY_OPEN = 123
CURLY_CLOSE = 125

SEPARATORS = [SPACE, CURLY_OPEN, CURLY_CLOSE]

# TODO: can we get this from some kind of config, so that we don't have to manually maintain this list here deep down??
SUBSTRUCTURE = ['cardinal', 'ordinal', 'decimal', 'time', 'date', 'connector', 'acronym', 'abbreviation', 'percent', 'telephone']

CLOSING_FIELD = '}'
TOKEN_LABEL = 'tokens'


class FSTParser:

    def __init__(self, utf8_symbols):
        self.fst = None
        self.state = 0
        self.last_state = 0
        self.inp_label = 0
        self.out_label = 0
        self.token_start = 0
        self.last_token_end = 0
        self.num_states = 0
        self.utf8_symbols = utf8_symbols
        #TODO: do we need this? Token name is set through value parsing, this field never used
        self.token_name = '' # does this belong here?


    def parse_tokens_from_fst(self, classified_fst, utt):
        """
        Parses tokens from the classified_fst, and updates the token information in the utterance: token types,
        names, etc.

        :param utt:
        :return:
        """
        self._init_fst(classified_fst)

        while self.state < self.fst.num_states() - 1:
            label = self._consume_label()
            if label != TOKEN_LABEL:
                #TODO: logging, error handling
                print('not tokens!')
                break
            self._next_state()
            token = Token()
            self._parse_fst(token)
            self._update_utterance(utt, token, False)

    #
    #  PRIVATE METHODS
    #

    def _init_fst(self, inp_fst):
        #TODO: error handling, e.g. by an empty fst?
        self.fst = inp_fst
        self.state = self.fst.start()
        self.last_state = self.fst.start()
        self.num_states = self.fst.num_states()

    def _update_utterance(self, utt, token, set_semiotic_class):
        #TODO: see what we really need from this - token indices etc.
        token_end = self.token_start + len(token.name)
        token.start_index = self.token_start
        self.last_token_end = token_end - 1
        token.end_index = self.last_token_end

        if token.has_word() and not token.token_type:
            token.set_wordid(token.word)
            token.set_token_type(TokenType.WORD)
        elif set_semiotic_class:
            token.set_token_type(TokenType.SEMIOTIC_CLASS)

        utt.ling_structure.tokens.append(token)

        self.token_start = token_end
        self.last_token_name = self.token_name
        self.token_name = ''

    def _parse_fst(self, tok, sem_class_label=None):
        # parses fst and sets token values (name, semiotic class)
        field_order = []

        while True:
            label = self._consume_label()
            #TODO: add safety condition - if we don't end with a } - then we have an endless loop
            if label == CLOSING_FIELD:
                return
            if label and not tok.has_semiotic_class():
                tok.set_semiotic_class(label)
                sem_class_label=label
            field_order.append(label)
            if label in SUBSTRUCTURE:
                self._next_state()
                self._parse_fst(tok, sem_class_label=label)
            elif label:
                value = self._parse_field_value()
                tok.set_value((label, value), sem_class_label)

        self._consume_whitespace()

    def _parse_field_value(self):

        value_arr = []
        while self._next_state():
            if self.out_label == QUOTES:
                value_arr = self._parse_quoted_field_value(value_arr)
            elif self.out_label == SPACE:
                return ''.join(value_arr)
            elif self.out_label == CURLY_CLOSE:
                self._prev_state() # unconsume the curly brace
                return ''.join(value_arr)
            elif self.out_label:
                value_arr.append(self.utf8_symbols.find(self.out_label).decode('utf-8'))

    def _parse_quoted_field_value(self, arr):

        while self._next_state():
            if self.out_label == EPSILON:
                continue
            if self.out_label != QUOTES:
                arr.append(self.utf8_symbols.find(self.out_label).decode('utf-8'))
            else:
                return arr

    def _consume_label(self):

        label_arr = []
        while self._next_state():
            if (self.out_label == SPACE and not label_arr) or self.out_label == EPSILON:
                continue
            elif not self._is_separator(self.out_label):
                label_arr.append(self.utf8_symbols.find(self.out_label).decode('utf-8'))
            elif self.out_label == CURLY_CLOSE and not label_arr:
                label_arr.append(self.utf8_symbols.find(self.out_label).decode('utf-8'))
                break
            else:
                #if self.out_label != COLON and self.out_label != SPACE:
                    # we are at the beginning of the next label, go to previous state to be able to
                    # start the parsing of the next label at the correct place
                   # self._prev_state()
                break

        self._consume_whitespace()
        return ''.join(label_arr)

    def _consume_whitespace(self):

        while self._next_state():
            if self.out_label != SPACE and self.out_label != EPSILON:
                self._prev_state()
                break

    def _next_state(self):
        # Moves to next state in the fst and updates labels, last state, state and token name
        # If we are already at the end, returns False

        arc_it = self.fst.arcs(self.state)
        if arc_it.done():
            return False

        self.inp_label = arc_it.value().ilabel
        self.out_label = arc_it.value().olabel

        if self.inp_label != EPSILON:
            # Don't aggregate leading whitespace against a token
            if self.inp_label == SPACE and not self.token_name:
                self.token_start += 1
            else:
                self.token_name += self.utf8_symbols.find(self.inp_label).decode('utf-8')

        self.last_state = self.state
        self.state = arc_it.value().nextstate

        return True

    def _prev_state(self):

        self.state = self.last_state
        # Undo any input aggregation we might have done
        if self.inp_label:
            if self.inp_label == SPACE and not self.token_name:
                self.token_start -= 1
            elif self.token_name:
                self.token_name = self.token_name[:-1]

    def _is_separator(self, elem):

        if elem in SEPARATORS:
            return True
        return False

