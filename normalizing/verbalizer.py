#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verbalize semiotic class tokens for an utterance.

"""
import pynini as pn
import copy
from timeit import default_timer as timer
import re
from fst_compiler import FST_Compiler
from utt_coll import TokenType
from verbalized import Verbalized


class Verbalizer:

    SIL = '<sil>'
    UNK = '<unk>'
    AND = 'og'
    SEPARATORS = ['komma', 'til']

    def __init__(self, path_to_grammar, path_to_lm, utf8_symbols, word_symbols):
        #TODO: error handling for grammar reading
        self.thrax_grammar = pn.Fst.read(path_to_grammar)
        self.thrax_grammar.arcsort()
        self.word_symbols = word_symbols
        start = timer()
        self.lm = pn.Fst.read(path_to_lm)
        self.lm.set_input_symbols(self.word_symbols)
        self.lm.set_output_symbols(self.word_symbols)
        self.lm.arcsort()
        end = timer()
        print('LM-loading: ' + str(end - start))
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
        if not tokens:
            print('No tokens for ' + utt.original_sentence)
            return
        verbalization = Verbalized()
        needs_disambiguation = False

        for tok in tokens:
            if tok.token_type == TokenType.SEMIOTIC_CLASS:
                words = self._verbalize_token(tok)
                needs_disambiguation = self._validate_verbalization(needs_disambiguation, tok, utt, words)
                if utt.reclassify:
                    return

            elif tok.token_type == TokenType.PUNCT:
                #words = [self.SIL]
                if len(tok.word) > 0:
                    #don't want to keep ',_,' in tagged mode, only ','
                    words = [tok.word[0]]
                else:
                    words = [tok.word]
            else:
                words = [tok.word]

            tok.set_verbalization_arr(words)
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
                if isinstance(elem, list):
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
        # TODO: for long patterns like 1992-1997 unrelated verbalizations can have the same length,
        # causing this method to deliver messed up results!
        for i in range(1, len(verb_arr)):
            elem_arr = verb_arr[i]
            for j in range(len(elem_arr)):
                if elem_arr[j] in result_arr[j]:
                    continue
                else:
                    result_arr[j].append(elem_arr[j])

        return result_arr

    @staticmethod
    def adjust_pos_for_one(wrd, pos):
        if wrd in ['einn', 'einum', 'eins', 'ein', 'eina', 'einni', 'einnar', 'eitt', 'einu']:
            pos = pos[:3] + 'f' + pos[-1]
        return pos

    def valid_pos_pattern(self, verbalization):
        if not '_' in verbalization:
            return True

        tokens = verbalization.split()
        pos_set = set()
        for tok in tokens:
            if '_' in tok:
                wrd, pos = tok.split('_')
                pos = self.adjust_pos_for_one(wrd, pos)
                pos_set.add(pos)
                if len(pos_set) > 1:
                    return False

        return len(pos_set) == 1

    #
    #  PRIVATE METHODS
    #

    def _validate_verbalization(self, needs_disambig, tok, utt, words):

        word_str = self.extract_string(words)
        if len(word_str) > 1 and word_str == tok.name and not utt.reclassify:
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
        ###############################
        # Baseline: no language model:
        #verbalized_no_lm = pn.shortestpath(verbalized_fst).optimize()
        #try:
        #    verbalized = verbalized_no_lm.stringify(token_type=self.utf8_symbols)
        #    verbal = verbalized.replace(' ', '')
        #    verbal = verbal.replace('0x0020', ' ')
        #    splitted_arr = [verbal]
        #    return splitted_arr
        #except Exception:
        #    splitted_arr = [token.word]
        #    return splitted_arr
        #
        ################################
        fst_size = verbalized_fst.num_states()
        splitted_arr = []
        if fst_size == 0:
            # no verbalization through thrax grammar
            print('no verbalization for ' + token.name)
            token.verbalization_failed = True
            for c in token.name:
                splitted_arr.append([c])
        else:
            res = verbalized_fst.paths(output_token_type=self.utf8_symbols).ostrings()
            p = list(res)
            verbalized_arr = []
            for elem in p:
                verbal = elem.replace(' ', '')
                verbal = verbal.replace('0x0020', ' ')
                #for mixed modus: ensure every number has the same pos, in a multi number token
                # 24. : tuttugustu_lvfnvf og fjórðu_lvfnvf and not: tuttugustu_lvfþvf og fjórðu_lvfnvf
                if self.valid_pos_pattern(verbal):
                    verbalized_arr.append(verbal)
            splitted_arr = self._split_verbalized_arr(verbalized_arr)

        return splitted_arr


    def _create_verbalized_fst(self, token):

        token_fst = self.compiler.fst_stringcompile_token(token)
        #token_fst.draw('token.dot')
        #self.thrax_grammar.draw('formatted_digits_grammar.dot')
        verbalized_fst = pn.compose(token_fst, self.thrax_grammar)
        fst_size = verbalized_fst.num_states()
        #verbalized_fst.draw('verbalized.dot')
        verbalized_fst.optimize()
        verbalized_fst.project(True)
        verbalized_fst.rmepsilon()
        #verbalized_fst.draw('verbalized_final.dot')

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
                # TODO: sure about that? nope ...
                #return verbalization_dict[k]
                #result_arr.append(verbalization_dict[k])
                inner_arr = []
                for v in verbalization_dict[k]:
                    inner_arr.append(v[0])
                result_arr.append([inner_arr])
            else:
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
        removed = False
        for sep in self.SEPARATORS:
            splitted = elem.split(sep)
            if len(splitted) == 2:
                arr = self._delete_and(splitted[0].split())
                arr2 = self._delete_and(splitted[1].split())
                arr.append(sep)
                arr.extend(arr2)
                removed = True
                break
        if not removed:
            arr = self._delete_and(elem.split())

        return arr

    def _delete_and(self, arr):
        DELETE = 'delete_me'

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
        replacement_dicts = {}
        for verbal_arr in verbalization.paths:
            shortest_path = self._language_model_scoring(verbal_arr)
            normalized_text = shortest_path.stringify(token_type=self.word_symbols)
            normalized[normalized_text] = pn.shortestdistance(shortest_path)
            replacement_dicts[normalized_text] = copy.deepcopy(self.replacement_dict)

        best_normalized = self._lowest_cost(normalized)
        #print("Best normalized: " + best_normalized)
        if best_normalized in replacement_dicts:
            best_normalized = self._insert_original_words(best_normalized, replacement_dicts[best_normalized])

        if self.oov_queue:
            #TODO: is this sufficient for multiple verbalizations?
            best_normalized = self._insert_original_oov(best_normalized, self.oov_queue)
            self.oov_queue = None



        return best_normalized


    def _lowest_cost(self, normalized):
        if len(normalized) == 1:
            return list(normalized.keys())[0]

        min_dist = 10000000  # random large number sure to exceed the best path cost of a verbalization
        best_verbalization = ''
        for k in normalized:
            # TODO: is the second weight maybe enough, no need to go through the whole wheights list?
            # seems that apart from the first weight (0.0), all weights of a path have the same cost.
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

        #word_fst, self.oov_queue = self.compiler.fst_stringcompile_words(verbal_arr)
        word_fst, self.replacement_dict = self.compiler.fst_stringcompile_words(verbal_arr)
        #self.replacement_dict = self.compiler.replacement_dict
        word_fst.set_output_symbols(self.word_symbols)
        word_fst.optimize()
        word_fst.project(True)
        word_fst.arcsort()
        #word_fst.draw('word_fst.dot')
        lm_intersect = pn.intersect(word_fst, self.lm)
        lm_intersect.optimize()
        #lm_intersect.draw('lm_intersect.dot')
        shortest_path = pn.shortestpath(lm_intersect).optimize()
        return shortest_path


    def _insert_original_oov(self, text, oov_dict):
        text_arr = text.split()
        for ind, wrd in enumerate(text_arr):
            if wrd != self.UNK:
                continue
            # if self._is_tag(wrd): need this?
            # if ind not in repl_dict:
            #    print("No replacement for " + wrd)
            # else:
            #    tag_map = repl_dict[ind]
            #    text_arr[ind] = tag_map[wrd]
            if ind in oov_dict:
                tag_map = oov_dict[ind]
                text_arr[ind] = tag_map[wrd]

        return ' '.join(text_arr)
        """
        for ind, wrd in enumerate(text_arr):
            if wrd == self.UNK:
                if self.oov_queue.empty():
                    print("OOV queue is empty - no replacement for <unk>!")
                else:
                    text_arr[ind] = self.oov_queue.get(False)
        return ' '.join(text_arr)
        """

    def _insert_original_words(self, text, repl_dict):
        text_arr = text.split()
        for ind, wrd in enumerate(text_arr):
            #if wrd == self.UNK:
            #    continue
            #if self._is_tag(wrd): need this?
            #if ind not in repl_dict:
            #    print("No replacement for " + wrd)
            #else:
            #    tag_map = repl_dict[ind]
            #    text_arr[ind] = tag_map[wrd]
            if ind in repl_dict:
                tag_map = repl_dict[ind]
                if wrd in tag_map:
                    text_arr[ind] = tag_map[wrd]

        return ' '.join(text_arr)

    def _is_tag(self, wrd):
        #is adjective tag
        if re.match('l[kvh][ef][noþe]vf', wrd):
            return True

        # is reduced adjective tag
        elif re.match('[kvh].*vf', wrd):
            print('found tag: ' + wrd)
            return True

        #is numeral tag
        elif re.match('tf[kvh][ef][noþe]', wrd):
            return True


        return False

