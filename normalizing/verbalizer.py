#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verbalize semiotic class tokens for an utterance.

"""
import pynini as pn
import graphs
from fst_compiler import FST_Compiler
from utt_coll import TokenType
from verbalized import Verbalized


class Verbalizer:

    SIL = 'sil'
    UNK = '<unk>'
    AND = 'og'

    def __init__(self, path_to_grammar, path_to_lm, utf8_symbols, word_symbols):
        #TODO: error handling for grammar reading
        self.thrax_grammar = pn.Fst.read(path_to_grammar)
        self.thrax_grammar.arcsort()
        self.word_symbols = word_symbols
        self.lm = pn.Fst.read(path_to_lm)
        self.lm.set_input_symbols(self.word_symbols)
        self.lm.set_output_symbols(self.word_symbols)
        self.lm.arcsort()
        self.utf8_symbols = utf8_symbols
        self.compiler = FST_Compiler(utf8_symbols, word_symbols)
        self.oov_queue = None


    def verbalize(self, utt):
        """
        Verbalizes/normalizes the classified structures from utt and sets the normalized_sentence attribute of utt
        to the normalized version of the original_sentence.

        :param utt:
        :return:
        """

        tokens = utt.ling_structure.tokens
        verbalization = Verbalized()
        needs_disambiguation = False

        for tok in tokens:
            if tok.token_type == TokenType.SEMIOTIC_CLASS:
                words = self._verbalize_token(tok)
                needs_disambiguation = self._validate_verbalization(needs_disambiguation, tok, utt, words)
                if utt.reclassify:
                    return

            elif tok.semiotic_class == TokenType.PUNCT:
                words = [self.SIL]
            else:
                words = [tok.word]

            verbalization.extend_paths(words)

        if needs_disambiguation or verbalization.max_depth > 1:
            verbalized = self.disambiguate(verbalization)

        else:
            verbalized_arr = [wrd for sublist in verbalization.paths[0] for wrd in sublist]
            verbalized = ' '.join(verbalized_arr)

        utt.normalized_sentence = verbalized

    @staticmethod
    def extract_string(arr):
        #TODO: util?
        # extracts a string from a depth-1 list, for nested lists returns an empty string
        res = []
        for a in arr:
            for elem in a:
                # do we have a list of lists?
                if len(elem[0]) > 1:
                    return ''
                res.append(elem)

        return ''.join(res)

    @staticmethod
    def _needs_splitting(arr):
        needs_splitting = False
        for elem in arr:
            if len(elem.split()) > 1:
                needs_splitting = True
                break

        return needs_splitting

    @staticmethod
    def split_to_dict(verbalization, verbalization_dict):
        arr = verbalization.split()
        if len(arr) in verbalization_dict:
            verbalization_dict[len(arr)].append(arr)
        else:
            verbalization_dict[len(arr)] = [arr]

    @staticmethod
    def _construct_splitted_arr(verb_arr):

        result_arr = []
        # construct the baseline list
        for elem in verb_arr[0]:
            result_arr.append([elem])
        # compare all other lists to the baseline, add words if different, do nothing if equal
        # (the lists have previously been tested for equal length)
        for i in range(1, len(verb_arr)):
            elem_arr = verb_arr[i]
            for j in range(len(elem_arr)):
                if elem_arr[j] in result_arr[j]:
                    continue
                else:
                    result_arr[j].append(elem_arr[j])

        return result_arr

    #
    #  PRIVATE METHODS
    #

    def _validate_verbalization(self, needs_disambig, tok, utt, words):

        word_str = self.extract_string(words)
        if word_str == tok.name and not utt.reclassify:
            # verbalization failed, we create a space separated token name
            # and mark the utterance for re-classification and verbalization
            tok.name = ' '.join(word_str)
            utt.reclassify = True

        elif len(words) > 1:
            needs_disambig = True

        return needs_disambig

    #
    # CREATE POSSIBLE VERBALIZATIONS FOR A TOKEN
    #

    def _verbalize_token(self, token):

        verbalized_fst = self._create_verbalized_fst(token)
        fst_size = verbalized_fst.num_states()
        splitted_arr = []
        if fst_size == 0:
            # no verbalization through thrax grammar
            print('no verbalization for ' + token.name)
            token.verbalization_failed = True
            for c in token.name:
                splitted_arr.append([c])
        else:
            verbalized_arr = graphs.extract_verbalization(verbalized_fst, self.utf8_symbols)
            splitted_arr = self._split_verbalized_arr(verbalized_arr)

        return splitted_arr


    def _create_verbalized_fst(self, token):

        token_fst = self.compiler.fst_stringcompile_token(token)
        verbalized_fst = pn.compose(token_fst, self.thrax_grammar)
        verbalized_fst.optimize()
        verbalized_fst.project(True)
        verbalized_fst.rmepsilon()

        return verbalized_fst


    def _split_verbalized_arr(self, verbalized_arr):

        # ['níu hundruð og tvö', 'níu hundruð og tvær', 'níu hundruð og tveir'] ->
        # [['níu'], ['hundruð'], ['og'], ['tvö', 'tvær', 'tveir']] (split into single words, combining same words to one arr)
        # ['tvö', 'tvær', 'tveir'] -> ['tvö', 'tvær', 'tveir'] (do nothing)
        # When the verbalizations are too different, builts a list of possible verbalizations:
        # ['tólf hundruð', 'þúsund tvö hundruð', 'þúsund tvær hundruð' 'eitt þúsund og tveir hundruð' ...]
        # -> [[['tólf'], ['hundruð']],
        #     [['þúsund'], ['tveir', 'tvær', 'tvö'], ['hundruð]],
        #     [[...]]]

        verbalized_arr = self._clean_connectors(verbalized_arr)
        if not self._needs_splitting(verbalized_arr):
            return verbalized_arr

        # create a dict of verbalizations, with the length of the verbalizations in words as key

        verbalization_dict = {}
        for verbalization in verbalized_arr:
            self.split_to_dict(verbalization, verbalization_dict)

        result_arr = []
        for k in verbalization_dict.keys():
            if k == 1:
                # TODO: sure about that?
                return verbalization_dict[k]
            inner_result_arr = self._construct_splitted_arr(verbalization_dict[k])
            result_arr.append(inner_result_arr)

        return result_arr


    def _clean_connectors(self, verbalization_arr):
        # For now we are dealing with AND/og in verbalized numbers. The grammar allows for e.g.
        # sjö hundruð og sjötíu og sjö (seven hundred and seventy and seven).
        # Delete superfluous 'og' and choose a version with 'og' in the last possible position,
        # as opposed to e.g. sjö hundruð og sjötíu sjö (which is a non-valid verbalization).

        result = []

        for elem in verbalization_arr:
            arr = self._remove_connectors(elem)
            result.append(' '.join(arr))

        for res in result:
            # now every string should have max one 'og' - choose the one with the 'og' in last possible position,
            # given that all other elements are equal, and remove the others
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


    def _remove_connectors(self, elem):

        DELETE = 'delete_me'
        arr = elem.split()

        if self.AND in arr and len(arr) > 3:
            last_and_index = len(arr) - arr[::-1].index(self.AND) - 1
            while arr.index(self.AND) != last_and_index:
                arr[arr.index(self.AND)] = DELETE
                if not self.AND in arr:
                    break

        while DELETE in arr:
            arr.remove(DELETE)

        return arr


    #
    # DISAMBIGUATE AND FINALIZE VERBALIZATION
    #

    def disambiguate(self, verbalization):
        normalized = {}
        for verbal_arr in verbalization.paths:
            shortest_path = self._language_model_scoring(verbal_arr)
            normalized_text = shortest_path.stringify(token_type=self.word_symbols)
            normalized[normalized_text] = pn.shortestdistance(shortest_path)

        best_normalized = self._lowest_cost(normalized)

        if self.oov_queue:
            #TODO: is this sufficient for multiple verbalizations?
            best_normalized = self._insert_original_oov(best_normalized)
            self.oov_queue = None

        return best_normalized


    def _lowest_cost(self, normalized):
        if len(normalized) == 1:
            return list(normalized.keys())[0]

        min_dist = 10000000  # random large number sure to exceed the best path cost of a verbalization
        best_verbalization = ''
        for k in normalized:
            # TODO: is the second weight maybe enough, no need to go through the whole wheights list?
            # seems that apart from the first wheight (0.0), all weights of a path have the same cost.
            sum = 0.0
            for i in range(len(normalized[k])):
                weight_as_bstring = normalized[k][i].to_string()
                s = weight_as_bstring.decode()
                weight_as_float = float(s)
                sum += weight_as_float
            avg_weight = sum / len(normalized[k])

            if avg_weight < min_dist:
                min_dist = avg_weight
                best_verbalization = k

        return best_verbalization


    def _language_model_scoring(self, verbal_arr):

        word_fst, self.oov_queue = self.compiler.fst_stringcompile_words(verbal_arr)
        word_fst.set_output_symbols(self.word_symbols)
        word_fst.optimize()
        word_fst.project(True)
        word_fst.arcsort()
        lm_intersect = pn.intersect(word_fst, self.lm)
        lm_intersect.optimize()
        shortest_path = pn.shortestpath(lm_intersect).optimize()
        return shortest_path


    def _insert_original_oov(self, text):
        text_arr = text.split()
        for ind, wrd in enumerate(text_arr):
            if wrd == self.UNK:
                if self.oov_queue.empty():
                    print("OOV queue is empty - no replacement for <unk>!")
                else:
                    text_arr[ind] = self.oov_queue.get(False)
        return ' '.join(text_arr)
