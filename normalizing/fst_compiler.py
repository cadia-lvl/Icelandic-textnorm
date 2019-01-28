#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Provides methods for FST stringcompile


"""
import queue
import pynini as pn
import pywrapfst as fst


class FST_Compiler:

    ATTR_DIV = '|'  # Division character between the elements of a classified token
    UNK = '<unk>'   # A placeholder for an unknown word

    def __init__(self, utf8_symbols, word_symbols):
        self.utf8_symbols = utf8_symbols
        self.word_symbols = word_symbols
        self.current_oov_queue = None
        self.replacement_dict = None


    def fst_stringcompile(self, text):
        """
        Compiles a string into a Pynini format FST, converting the characters of 'text' into their utf8 integer
        representation.

        :param text:
        :return: an FST in Pynini format
        """

        input_fst = self._get_basic_fst(text)
        # conversion to Pynini format necessary for the access of Pynini FST methods
        pynini_fst = pn.Fst.from_pywrapfst(input_fst)

        return pynini_fst


    def fst_stringcompile_words(self, text_arr):
        """
        Compiles a string into a Pynini format FST, converting the words in 'text_arr' into their integer
        representations according to word-symbol table.

        :param text_arr:
        :return:
        """
        #input_fst = self._get_basic_word_fst(text_arr)
        input_fst = self._get_basic_tag_fst(text_arr)
        pynini_fst = pn.Fst.from_pywrapfst(input_fst)

        return pynini_fst, self.current_oov_queue


    def fst_stringcompile_token(self, token):
        """
        Compiles the content of the semiotic class of 'token' into an FST in Pynini format.

        Example: Token has semiotic class 'cardinal' with the content '5':
        The labels of the resulting FST (with utf8 integer representation of the characters):

        99:99 - 97:97 - 114:114 - 100:100 - 105:105 - 110:110 - 97:97 - 108:108 - 124:124 - 0:0 -
        105:105 - 110:110 - 116:116 - 101:101 - 103:103 - 101:101 - 114:114 - 58:58 - 0:0 - 53:53 - 0:0 - 124:124: 0:0

        [c - a - r - d - i - n - a - l - | - ' ' - i - n - t - e - g - e - r - : - ' ' - 5 - ' ' - | - ' ']


        :param token: a labeled token (semiotic class)
        :return: an FST representation of the token classification
        """

        if not token.semiotic_class:
            # logger warn or error?
            print('fst_compiler.fst_stringcompile_token(): Token ' + str(token) + ' does not have a semiotic class!')
            return

      #  semiotic_class = token.semiotic_class.name + self.ATTR_DIV
      #  label_fst = self._get_basic_fst(semiotic_class)
      #  last_attr_fst = None
      #  for attr in token.semiotic_class.grammar_attributes():
      #      attr_str = ' '.join(attr) + ' ' + self.ATTR_DIV + ' '
      #      attr_fst = self._get_basic_fst(attr_str, unknown_to_zero=True)
      #      # for semiotic classes having more than one attribute, e.g. decimal: integer_part and fractional_part
      #      if last_attr_fst:
      #          pn_attr = pn.Fst.from_pywrapfst(attr_fst)
      #          last_attr_fst = pn.Fst.concat(last_attr_fst, pn_attr)
      #      else:
      #          last_attr_fst = pn.Fst.from_pywrapfst(attr_fst)

        token_string = token.semiotic_class.serialize_to_string()
        print(token_string)
        token_fst = self._get_basic_fst(token_string, unknown_to_zero=True)
        pynini_fst = pn.Fst.from_pywrapfst(token_fst)
        #pn_label = pn.Fst.from_pywrapfst(label_fst)
        #pn_attr = pn.Fst.from_pywrapfst(last_attr_fst)
        #input_fst = pn.Fst.concat(pn_label, pn_attr)
        #pynini_fst = pn.Fst.from_pywrapfst(input_fst)

        return pynini_fst


    #
    # PRIVATE METHODS
    #

    def _get_basic_fst(self, text, unknown_to_zero=False):
        """
        Compiles a string into an OpenFST format FST, converting the characters of 'text' into their
        utf8 integer representation.
        The space character is not included in the utf8 symbol table and is per default converted into '0x0020'.
        If unknown_to_zero is set to True, unknown chars will be converted to zero.

        :param text: the string to compile into an FST
        :param unknown_to_zero: False per default
        :return: an OpenFST format FST representing 'text'
        """

        compiler = fst.Compiler()
        state_counter = 0
        for c in text:
            int_val = self._get_int_value(c, unknown_to_zero)
            from_state = state_counter
            to_state = state_counter + 1
            self._compile_entry(compiler, from_state, int_val, to_state)
            state_counter += 1

        compiler.write("{}\n\n".format(state_counter))

        input_fst = compiler.compile()
        return input_fst


    def _get_basic_word_fst(self, text_arr):

        self.current_oov_queue = queue.Queue()
        compiler = fst.Compiler()
        state_counter = 0
        next_state = 0

        for arr in text_arr:
            if not arr:
                continue
            # single word, single expansion
            if len(arr) == 1:
                for w in arr:
                    int_val = self._get_int_value_word(w)
                    from_state = state_counter
                    if next_state != 0:
                        to_state = next_state
                        state_counter = next_state - 1
                        next_state = 0
                    else:
                        to_state = state_counter + 1
                    self._compile_entry(compiler, from_state, int_val, to_state)
                    state_counter += 1

            # multiple verbalization possibilities
            # we are working char by char, so store the state_counter, such that
            # all possibilities have the same from_state (starting state)
            else:
                from_state = state_counter
                to_state = state_counter + 1
                for i, w in enumerate(arr):
                    int_val = self._get_int_value_word(w)
                    self._compile_entry(compiler, from_state, int_val, to_state)
                    state_counter += 1

                next_state = to_state + 1
                state_counter = to_state

        compiler.write("{}\n\n".format(state_counter))

        input_fst = compiler.compile()
        return input_fst

    def _get_basic_tag_fst(self, text_arr):
        # create an fst from text_arr, extracting pos-tags where applicable
        # only use pos-tags where found, store the words for reconstruction of the utterance
        self.current_oov_queue = queue.Queue()
        self.replacement_dict = {}
        compiler = fst.Compiler()
        state_counter = 0
        next_state = 0

        for i, arr in enumerate(text_arr):
            if not arr:
                continue
            # single word, single expansion
            if len(arr) == 1:
                for w in arr:
                    if '_' in w:
                        wrd = w[:w.index('_')]
                        w = w[w.index('_') + 1:]
                        if i in self.replacement_dict:
                            d = self.replacement_dict[i]
                            d[w] = wrd
                        else:
                            self.replacement_dict[i] = {}
                            d = self.replacement_dict[i]
                            d[w] = wrd

                    int_val = self._get_int_value_word(w)
                    from_state = state_counter
                    if next_state != 0:
                        to_state = next_state
                        state_counter = next_state - 1
                        next_state = 0
                    else:
                        to_state = state_counter + 1
                    self._compile_entry(compiler, from_state, int_val, to_state)
                    state_counter += 1

            # multiple verbalization possibilities
            # we are working char by char, so store the state_counter, such that
            # all possibilities have the same from_state (starting state)
            else:
                from_state = state_counter
                to_state = state_counter + 1
                for w in arr:
                    if '_' in w:
                        wrd = w[:w.index('_')]
                        w = w[w.index('_') + 1:]
                        if i in self.replacement_dict:
                            d = self.replacement_dict[i]
                            d[w] = wrd
                        else:
                            self.replacement_dict[i] = {}
                            d = self.replacement_dict[i]
                            d[w] = wrd
                    int_val = self._get_int_value_word(w)
                    self._compile_entry(compiler, from_state, int_val, to_state)
                    state_counter += 1

                next_state = to_state + 1
                state_counter = to_state

        compiler.write("{}\n\n".format(state_counter))

        input_fst = compiler.compile()
        return input_fst

    def _get_int_value(self, character, unknown_to_zero):

        int_val = self.utf8_symbols.find(character)
        if int_val == -1:
            # character is unknown, not found in utf8_symbols
            if unknown_to_zero:
                int_val = 0
            elif ord(character) <= 32:
                # For a space (' ') we extract the hex repr: 0x0020 with 2 trailing zeros.
                # Captures non-printable chars as well, but we really don't handle them when verbalizing
                # since we haven't 'met' them yet - fix that, if necessary
                conv = '0x%04x' % ord(character)
                int_val = self.utf8_symbols.find(conv)
            else:
                # TODO: logging, error handling, here? Propagate the -1 value?
                print('No int value found for ' + character)

        return int_val

    def _get_int_value_word(self, word):

        int_val = self.word_symbols.find(word)
        if int_val == -1:
            int_val = self.word_symbols.find(self.UNK)
            self.current_oov_queue.put(word)

        return int_val

    def _compile_entry(self, compiler, from_state, int_val, to_state):

        entry = "{} {} {} {}\n".format(from_state, to_state, int_val, int_val)
        compiler.write(entry)
