#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import jsonpickle
from enum import Enum
from utterance_structure.semiotic_classes import *

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
        self.reclassify = False

    def get_test_output(self):
        test_output = []
        original_input = self.original_sentence.split()
        normalized_output = self.normalized_sentence.split()
        org_ind = 0
        norm_ind = 0
        for ind, tok in enumerate(self.ling_structure.tokens):
            current_verbalization = []
            if len(tok.verbalization_arr) == 1 and not isinstance(tok.verbalization_arr[0], list):
                if tok.token_type == TokenType.WORD:
                    verbalization = tok.name
                    if original_input[org_ind] != verbalization:
                        print(original_input[org_ind] + ' ' + verbalization)
                else:
                    verbalization = tok.verbalization_arr[0]
                if org_ind >= len(original_input):
                    test_output.append('' + '\t' + verbalization)
                else:
                    test_output.append(original_input[org_ind] + '\t' + verbalization)
                org_ind += 1
                norm_ind += 1
            elif isinstance(tok.verbalization_arr[0], list):
                # multiword verbalization, possibly also multiple possibilities per word
                if org_ind >= len(original_input):
                    current_input_token = ''
                else:
                    current_input_token = original_input[org_ind] #180°C

                for verbal_arr in tok.verbalization_arr:

                    #verbal_arr = tok.verbalization_arr[0]
                    tok_count = 0
                    for arr in verbal_arr:
                        #[eitt_abc, einn_def, ...]
                        current_normalized = normalized_output[norm_ind]
                        for wrd in arr:
                            if '_' in wrd:
                                wrd = wrd[:wrd.index('_')]
                            if wrd == current_normalized:
                                current_verbalization.append(wrd)
                                norm_ind = norm_ind + 1
                                tok_count += 1
                                break

                    if tok_count == len(verbal_arr):
                        #already found a full match
                        break
                    else:
                        # we might have followed a wrong path, start over
                        current_verbalization = []

                test_output.append(current_input_token + '\t' + ' '.join(current_verbalization))
                org_ind += 1

            else:
                # one word but multiple possibilities in verbalization
                if org_ind >= len(original_input):
                    current_input_token = ''
                else:
                    current_input_token = original_input[org_ind]  # 180°C
                current_normalized = normalized_output[norm_ind]  # eitt
                for wrd in tok.verbalization_arr:
                    if '_' in wrd:
                        wrd = wrd[:wrd.index('_')]
                    if wrd == current_normalized:
                        current_verbalization.append(wrd)
                        norm_ind = norm_ind + 1
                        #current_normalized = normalized_output[norm_ind]
                        break

                test_output.append(current_input_token + '\t' + ' '.join(current_verbalization))
                org_ind += 1
               # norm_ind += 1

        test_output.append('####\t####')
        return '\n'.join(test_output)

    #def to_jsonpickle(self, filename):
    #    json_enc = jsonpickle.encode(self)
    #    with open(filename, 'w') as f:
    #        f.write(json_enc)

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
        self.verbalization_arr = []
        self.verbalization_failed = False
        self.start_index = 0
        self.end_index = 0

    def set_token_type(self, token_type):
        self.token_type = token_type

    #def set_semiotic_class(self, sem_class):
    #    self.semiotic_class = sem_class

    def set_semiotic_class(self, label):
        self.semiotic_class = SemioticClasses(label).semiotic_class
        if self.semiotic_class:
            self.set_token_type(TokenType.SEMIOTIC_CLASS)

    def set_name(self, name):
        self.name = name
        #if self.name:
        #    self.name += '0x0020' + name
        #else:
        #    self.name = name

    def append_to_word(self, wrd):
        self.word += wrd

    def set_wordid(self, wid):
        self.wordid = wid

    def set_pause_length(self, pl):
        self.pause_length = pl

    def set_phrase_break(self, pb):
        self.phrase_break = pb

    def set_verbalization_arr(self, v_arr):
        self.verbalization_arr = v_arr

    def has_word(self):
        if self.word:
            return True
        return False

    def has_semiotic_class(self):
        if self.semiotic_class:
            return True
        return False

    def set_value(self, tuple, sem_class_label):
        #self.name = value
        label = tuple[0]
        value = tuple[1]
        # TODO: what are we going to do with this? what is name and what is word?
        if self.valid_word(value):
            self.set_name(value)
            self.append_to_word(value)

        if label == 'pause_length:':
            if value == 'PAUSE_SHORT':
                self.pause_length = PauseLength.PAUSE_SHORT
            elif value == 'PAUSE_MEDIUM':
                self.pause_length = PauseLength.PAUSE_MEDIUM
            elif value == 'PAUSE_LONG':
                self.pause_length = PauseLength.PAUSE_LONG

        if label == 'phrase_break:':
            if value == 'true':
                self.phrase_break = True

        if label == 'type:':
            if value == 'PUNCT':
                self.token_type = TokenType.PUNCT

        if self.semiotic_class and sem_class_label:
            self.semiotic_class.set_attribute(tuple, sem_class_label)

            # add to existing object
            #if isinstance(self.semiotic_class, utterance_structure.semiotic_classes.Decimal):
            #    if 'fractional_part:' in tuple:
            #        self.semiotic_class.set_fractional_part(tuple['fractional_part:'])
             #   elif sem_class_label == 'percent':
             #       updated_semclass = utterance_structure.semiotic_classes.Percent()
             #       if 'symbol:' in tuple:
             #           updated_semclass.set_symbol(tuple['symbol:'])
             #           updated_semclass.set_decimal(self.semiotic_class)
             #           self.semiotic_class = updated_semclass

           # elif isinstance(self.semiotic_class, utterance_structure.semiotic_classes.Time):
           #     if 'minutes:' in tuple:
            #        self.semiotic_class.set_minutes(tuple['minutes:'])

            #elif isinstance(self.semiotic_class, utterance_structure.semiotic_classes.Date):
            #    if 'month:' in tuple:
             #       self.semiotic_class.set_month(tuple['month:'])

            #elif isinstance(self.semiotic_class, utterance_structure.semiotic_classes.Acronym):
            #    if 'tail:' in tuple:
            #        self.semiotic_class.set_tail(tuple['tail:'])

        #elif sem_class_label:
         #   self.semiotic_class = self.get_semiotic_class(sem_class_label, tuple)
          #  self.token_type = TokenType.SEMIOTIC_CLASS

    def valid_word(self, wrd):

        if wrd in ['PAUSE_SHORT', 'PAUSE_MEDIUM', 'PAUSE_LONG', 'true', 'PUNCT']:
            return False
        return True


    """
    def get_semiotic_class(self, label, content):

        if label == 'cardinal':
            return utterance_structure.semiotic_classes.Cardinal(content['integer:'])
        if label == 'ordinal':
            return utterance_structure.semiotic_classes.Ordinal(content['integer:'])
        if label == 'decimal':
            decim = utterance_structure.semiotic_classes.Decimal()
            if 'integer_part:' in content:
                decim.set_integer_part(content['integer_part:'])
                return decim
            else:
                # Error
                print('We should have integer_part as initial field in a decimal!')

        if label == 'time':
            decim = utterance_structure.semiotic_classes.Time()
            if 'hours:' in content:
                decim.set_hours(content['hours:'])
                return decim
            else:
                # Error
                print('We should have hours as initial field in time!')

        if label == 'date':
            d = utterance_structure.semiotic_classes.Date()
            if 'day:' in content:
                d.set_day(content['day:'])
                return d
            else:
                # Error
                print('We should have day as initial field in date!')

        if label == 'acronym':
            d = utterance_structure.semiotic_classes.Acronym()
            if 'head:' in content:
                d.set_head(content['head:'])
                return d
            else:
                # Error
                print('We should have head as initial field in acronym!')

        if label == 'abbreviation':
            d = utterance_structure.semiotic_classes.Abbreviation()
            if 'abbr:' in content:
                d.set_abbreviation(content['abbr:'])
                return d
            else:
                # Error
                print('We should have abbreviation as initial field in abbreviation!')

        if label == 'percent':
            d = utterance_structure.semiotic_classes.Percent()
"""

    def print(self):
        print('TokenType: ' + str(self.token_type))
        print('Semiotic class: ' + str(self.semiotic_class))
        print('Name: ' + self.name)
        print('Word: ' + self.word)
        print('Pause length: ' + str(self.pause_length))
        print('Phrase break: ' + str(self.phrase_break))






