#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verbalize a semiotic class token.

"""
import queue
import pynini as pn
import semiotic_classes
from fst_compiler import FST_Compiler
from utt_coll import Token
from utt_coll import TokenType


class Verbalizer:

    def __init__(self, path_to_grammar, path_to_lm, utf8_symbols, word_symbols):
        self.thrax_grammar = pn.Fst.read(path_to_grammar)
        self.thrax_grammar.arcsort()
        self.word_symbols = word_symbols
        self.lm = pn.Fst.read(path_to_lm)
        self.lm.set_input_symbols(self.word_symbols)
        self.lm.set_output_symbols(self.word_symbols)
        self.lm.arcsort()

        self.compiler = FST_Compiler(utf8_symbols, word_symbols)
        self.sil = 'sil'
        self.unk = '<unk>'
        self.oov_queue = queue.Queue()

    def verbalize(self, utt):
        tokens = utt.ling_structure.tokens
        sentence_arr = []
        needs_disambiguation = False
        for tok in tokens:
            if tok.token_type == TokenType.SEMIOTIC_CLASS:
                words = self.verbalize_token(tok)
                if len(words) > 1:
                    needs_disambiguation = True
            elif tok.semiotic_class == TokenType.PUNCT:
                words = [self.sil]
            else:
                words = [tok.word]

            # make sure we flatten out possible nested lists
            list_to_append = list(filter(lambda x: isinstance(x, list), words))
            if list_to_append:
                for elem in list_to_append:
                    sentence_arr.append(elem)
            else:
                sentence_arr.append(words)

        print(str(sentence_arr))

        if needs_disambiguation:
            verbalized = self.disambiguate(sentence_arr)

        else:
            verbalized_arr = [wrd for sublist in sentence_arr for wrd in sublist]
            verbalized = ' '.join(verbalized_arr)

        utt.normalized_sentence = verbalized

    def verbalize_token(self, token):
        verbalized_fst = self.create_verbalized_fst(token)
        # TODO: fall back mechanism when verbalizing grammar fails, resulting in an empty FST
        verbalized_arr, self.oov_queue = self.compiler.extract_verbalization(verbalized_fst)
        single_words_arr = self.split_verbalized_arr(verbalized_arr)
        return single_words_arr

    def create_verbalized_fst(self, token):
        token_fst = self.compiler.fst_stringcompile_token(token)
        token_fst.draw('token.dot')
        verbalized_fst = pn.compose(token_fst, self.thrax_grammar)
        verbalized_fst.draw('verbalized.dot')
        verbalized_fst.optimize()
        verbalized_fst.draw('optimized.dot')
        verbalized_fst.project(True)
        verbalized_fst.draw('projected.dot')
        verbalized_fst.rmepsilon()
        verbalized_fst.draw('no_epsilon.dot')
        return verbalized_fst

    def split_verbalized_arr(self, verbalized_arr):
        # ['níu hundruð og tvö', 'níu hundruð og tvær', 'níu hundruð og tveir'] ->
        # [['níu'], ['hundruð'], ['og'], ['tvö', 'tvær', 'tveir']] (split into single words)
        # ['tvö', 'tvær', 'tveir'] -> ['tvö', 'tvær', 'tveir'] (do nothing)

        # TODO: control for same length of all arrays
        result_arr = []
        if len(verbalized_arr[0].split()) == 1:
            return verbalized_arr
        for elem in verbalized_arr[0].split():
            result_arr.append([elem])

        for i in range(1, len(verbalized_arr)):
            elem_arr = verbalized_arr[i].split()
            for j in range(len(elem_arr)):
                if result_arr[j][0] == elem_arr[j]:
                    continue
                else:
                    result_arr[j].append(elem_arr[j])

        return result_arr

    def insert_original_oov(self, text):
        text_arr = text.split()
        for ind, wrd in enumerate(text_arr):
            if wrd == self.unk:
                text_arr[ind] = self.oov_queue.get()
        return ' '.join(text_arr)

    def disambiguate(self, sent_arr):
        # TODO: language model disambiguation
        word_fst, self.oov_queue = self.compiler.fst_stringcompile_words(sent_arr)
        word_fst.draw('verb.dot')
        word_fst.set_output_symbols(self.word_symbols)
        word_fst.optimize()
        word_fst.project(True)
        word_fst.arcsort()
        word_fst.draw('verb_final.dot')  # tveir:tveir
        best_exp = pn.intersect(word_fst, self.lm)
        best_exp.optimize()
        best_exp.draw('best.dot')
        shortest_path = pn.shortestpath(best_exp).optimize()
        normalized_text = shortest_path.stringify(token_type=self.word_symbols)
        if self.oov_queue:
            normalized_text = self.insert_original_oov(normalized_text)
        print(normalized_text)

        return normalized_text

def main():

    verb = Verbalizer()
    token = Token()
    token.semiotic_class = semiotic_classes.Cardinal('22')
    result_arr = verb.verbalize_token(token)
    print(str(result_arr))



if __name__ == '__main__':
    main()