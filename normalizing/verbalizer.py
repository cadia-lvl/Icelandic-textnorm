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
from verbalized import Verbalized


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
        self.AND = 'og'
        self.oov_queue = None

    def extract_string(self, arr):
        res = []
        for a in arr:
            for elem in a:
                #do we have a list of lists?
                if len(elem[0]) > 1:
                    return ''
                res.append(elem)

        return ''.join(res)

    def verbalize(self, utt):
        tokens = utt.ling_structure.tokens
        #sentence_arr = []
        verbalization = Verbalized()
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

            # make sure we flatten out possible nested lists or create more lists, if we have different length
            # verbalization possibilities []
            verbalization.extend_paths(words)

        verbalization.print()

        if utt.reclassify:
            return

        if needs_disambiguation or verbalization.max_depth > 1:
            verbalized = self.disambiguate(verbalization)

        else:
            verbalized_arr = [wrd for sublist in verbalization.paths[0] for wrd in sublist]
            verbalized = ' '.join(verbalized_arr)

        utt.normalized_sentence = verbalized

    def verbalize_token(self, token):
        verbalized_fst = self.create_verbalized_fst(token)
        fst_size = verbalized_fst.num_states()
        single_words_arr = []
        if fst_size == 0:
            # no verbalization through thrax grammar
            print('no verbalization for ' + token.name)
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
        # can be much more complicated:
        # ['tólf hundruð', 'þúsund tvö hundruð', 'þúsund tvær hundruð' 'eitt þúsund og tveir hundruð' ...]
        # -> different number of words, different words

        verbalized_arr = self.delete_superfluous_and(verbalized_arr)
        needs_splitting = False
        for elem in verbalized_arr:
            if len(elem.split()) > 1:
                needs_splitting = True
                break

        if not needs_splitting:
            return verbalized_arr

        # create a dict of verbalizations, with the length of the verbalizations in words as key

        result_arr = []
        verbalization_dict = {}
        for verbalization in verbalized_arr:
            arr = verbalization.split()
            if len(arr) in verbalization_dict:
                verbalization_dict[len(arr)].append(arr)
            else:
                verbalization_dict[len(arr)] = [arr]

        for k in verbalization_dict.keys():
            if k == 1:
                return verbalization_dict[k]
            inner_result_arr = []
            print(str(verbalization_dict[k]))
            verb_arr = verbalization_dict[k]
            for elem in verb_arr[0]:
                inner_result_arr.append([elem])
            for i in range(1, len(verb_arr)):
                elem_arr = verb_arr[i]
                for j in range(len(elem_arr)):
                    if elem_arr[j] in inner_result_arr[j]:
                        continue
                    else:
                        inner_result_arr[j].append(elem_arr[j])

            result_arr.append(inner_result_arr)
        return result_arr

    def delete_superfluous_and(self, verbalization_arr):
        DELETE = 'delete_me'
        result = []
        for elem in verbalization_arr:
            arr = elem.split()
            if self.AND in arr and len(arr) > 3:
                last_and_index = len(arr)-arr[::-1].index(self.AND)-1
                while arr.index(self.AND) != last_and_index:
                    arr[arr.index(self.AND)] = DELETE
                    if not self.AND in arr:
                        break

            while DELETE in arr:
                arr.remove(DELETE)

            result.append(' '.join(arr))

        for res in result:
            # now every string should have max one 'og' - choose the one with the 'og' in last position,
            # given that all other elements are equal
            for r in result:
                diff = [i for i in res.split() if i not in r.split()]
                if diff == [self.AND]:
                    result[result.index(r)] = ''
                elif not diff:
                    if self.AND in r and self.AND in res:
                        if res.index(self.AND) > r.index(self.AND):
                            result[result.index(r)] = ''

        while '' in result:
            result.remove('')

        return result

    def insert_original_oov(self, text):
        text_arr = text.split()
        for ind, wrd in enumerate(text_arr):
            if wrd == self.unk:
                if self.oov_queue.empty():
                    print("OOV queue is empty - no replacement for <unk>!")
                else:
                    text_arr[ind] = self.oov_queue.get(False)
        return ' '.join(text_arr)

    def disambiguate(self, verbalization):
        normalized = {}
        for verbal_arr in verbalization.paths:

            word_fst, self.oov_queue = self.compiler.fst_stringcompile_words(verbal_arr)
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
            normalized[normalized_text] = pn.shortestdistance(shortest_path)
            #normalized[normalized_text] = shortest_path.final(shortest_path.num_states()-1)

        min_dist = 100000
        min_key = ''
        for k in normalized:
            sum = 0.0
            for i in range(len(normalized[k])):
                weight_as_bstring = normalized[k][i].to_string()
                s = weight_as_bstring.decode()
                weight_as_float = float(s)
                sum += weight_as_float
            avg_weight = sum/len(normalized[k])

            if avg_weight < min_dist:
                min_dist = avg_weight
                min_key = k

            print(k + ': ' + str(avg_weight))


        if self.oov_queue:
            min_key = self.insert_original_oov(min_key)
            self.oov_queue = None
        print(min_key)

        return min_key

def main():

    verb = Verbalizer()
    token = Token()
    token.semiotic_class = semiotic_classes.Cardinal('22')
    result_arr = verb.verbalize_token(token)
    print(str(result_arr))



if __name__ == '__main__':
    main()