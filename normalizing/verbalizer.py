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
        self.oov_queue = None

    def extract_string(self, arr):
        res = []
        for a in arr:
            for elem in a:
                res.append(elem)

        return ''.join(res)

    def verbalize(self, utt):
        tokens = utt.ling_structure.tokens
        sentence_arr = []
        needs_disambiguation = False
        for tok in tokens:
            if tok.token_type == TokenType.SEMIOTIC_CLASS:
                words = self.verbalize_token(tok)
                word_str = self.extract_string(words)
                if word_str == tok.name and not utt.reclassify:
                    #verbalization failed, we just have space separated token name
                    tok.name = ' '.join(word_str)
                    utt.reclassify = True
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

        if utt.reclassify:
            return

        if needs_disambiguation:
            verbalized = self.disambiguate(sentence_arr)

        else:
            verbalized_arr = [wrd for sublist in sentence_arr for wrd in sublist]
            verbalized = ' '.join(verbalized_arr)

        utt.normalized_sentence = verbalized

    def verbalize_token(self, token):
        verbalized_fst = self.create_verbalized_fst(token)
        fst_size = verbalized_fst.num_states()
        single_words_arr = []
        if fst_size == 0:
            # no verbalization through thrax grammar
            print('no verbalization for ' + token.name)
            # TODO: need to classify the utt again with separated tokens (0 4 instead of 04 for example)
            # how to do that, without getting stuck in an endless loop - one more try is ok, but then we have
            # to make sure we return a result. Think of this while refactoring
            token.verbalization_failed = True
            for c in token.name:
                single_words_arr.append([c])
        else:
            verbalized_arr = self.compiler.extract_verbalization(verbalized_fst)
            single_words_arr = self.split_verbalized_arr(verbalized_arr)
        return single_words_arr

    def create_verbalized_fst(self, token):
        token_fst = self.compiler.fst_stringcompile_token(token)
        token_fst.draw('token.dot')
        self.thrax_grammar.draw('thraxgrammar.dot')
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

        result_arr = []
        sorted_arr = sorted(verbalized_arr, key=lambda x: len(x), reverse=True)
        if len(sorted_arr[0].split()) == 1:
            return verbalized_arr
        # this might to be specialized: if we have multiple occurences of 'og', only keep the last:
        # sjö hundruð og sjötíu og sjö - delete the first 'og'
        sorted_arr = self.check_multiple_ands(sorted_arr)
        for elem in sorted_arr[0].split():
            result_arr.append([elem])

        for i in range(1, len(sorted_arr)):
            elem_arr = sorted_arr[i].split()
            for j in range(len(elem_arr)):
                if elem_arr[j] in result_arr[j]:
                    continue
                else:
                    result_arr[j].append(elem_arr[j])

        return result_arr

    def check_multiple_ands(self, arr):
        #TODO: does not work - have to align arrays!
        # see e.g. eitt þúsund og tvö hundruð vs. tólf hundruð
        AND = 'og'
        result_set = set()
        smallest_dist_from_end = 10000 # arbitrarily high number larger than a possible sentence word count
        found_AND = False
        for verbalized in arr:
            clean_arr = []
            a = verbalized.split()
            print(str(a))
            indices = [i for i, x in enumerate(a) if x == AND]
            if len(indices) > 1:
                last_index = indices[-1]
                if len(a) - last_index < smallest_dist_from_end:
                    smallest_dist_from_end = len(a) - last_index

            for ind in indices:
                found_AND = True
                if len(a) - ind > smallest_dist_from_end:
                    a[ind] = ''

            if found_AND and not AND in a:
                # if there is a possibility for an 'and', this is correct and thus a version completely without 'and'
                # should not be considered (like 'sjö hundruð sjötíu' instead of 'sjö hundruð og sjötíu'
                continue

            for elem in a:
                if len(elem) > 0:
                    clean_arr.append(elem)

            result_set.add(' '.join(clean_arr))

        return list(result_set)

    def insert_original_oov(self, text):
        text_arr = text.split()
        for ind, wrd in enumerate(text_arr):
            if wrd == self.unk:
                if self.oov_queue.empty():
                    print("OOV queue is empty - no replacement for <unk>!")
                else:
                    text_arr[ind] = self.oov_queue.get(False)
        return ' '.join(text_arr)

    def disambiguate(self, sent_arr):

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
            self.oov_queue = None
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