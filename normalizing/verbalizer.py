#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verbalize a semiotic class token.

"""

import pynini as pn
import semiotic_classes
from fst_compiler import FST_Compiler
from utt_coll import Token
from utt_coll import TokenType


class Verbalizer:

    def __init__(self, path_to_grammar='/Users/anna/sparrowhawk/sparrowhawk/documentation/grammars/ice/verbalize_serialization/ALL'):
        self.thrax_grammar = pn.Fst.read(path_to_grammar)
        self.thrax_grammar.arcsort()
        self.compiler = FST_Compiler()
        self.sil = 'sil'

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
                words = ['sil']
            else:
                words = [tok.word]
            sentence_arr.append(words)

        if needs_disambiguation:
            verbalized = self.disambiguate(sentence_arr)

        else:
            verbalized_arr = [wrd for sublist in sentence_arr for wrd in sublist]
            verbalized = ' '.join(verbalized_arr)

        utt.normalized_sentence = verbalized

    def verbalize_token(self, token):
        verbalized_fst = self.create_verbalized_fst(token)
        # TODO: fall back mechanism when verbalizing grammar fails, resulting in an empty FST
        verbalized_arr = self.compiler.extract_verbalization(verbalized_fst)

        return verbalized_arr

    def create_verbalized_fst(self, token):
        token_fst = self.compiler.fst_stringcompile_token(token)
        verbalized_fst = pn.compose(token_fst, self.thrax_grammar)
        verbalized_fst.optimize()
        verbalized_fst.project(True)
        verbalized_fst.rmepsilon()
        return verbalized_fst

    def disambiguate(self, sent_arr):
        # TODO: language model disambiguation
        verbalized_arr = [wrd for sublist in sent_arr for wrd in sublist]
        verbalized = ' '.join(verbalized_arr)
        return verbalized

def main():

    verb = Verbalizer()
    token = Token()
    token.semiotic_class = semiotic_classes.Cardinal('22')
    result_arr = verb.verbalize_token(token)
    print(str(result_arr))



if __name__ == '__main__':
    main()