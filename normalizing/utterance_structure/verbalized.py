#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stores all different verbalizing options for an utterance.

"""

class Verbalized:

    def __init__(self):
        self.paths = []
        self.max_depth = 0

    def add_path(self, path):
        self.paths.append(path)

    def extend_paths(self, token_verbalizations):
        """
        Extends paths with the token verbalizations that can be:
        a) an array of len 1, with only one word in the containing array (non-ambiguous verbalization/token type WORD)
        b) an array of len >= 1, where at least one of the arrays has more than one entries
        c) an array containing a list of arrays, for non-compatible verbalization paths

        a) ['fimm'] (5)
        b) [['tuttugu'],['og'],['tvo', 'tvær', 'tveir', 'tveimur', 'tveggja']] (22)
        c) [[['tólf'], ['hundruð']],
            [['eitt'], ['þúsund'], ['og'], ['tvo', 'tvær', 'tveir', 'tveimur', 'tveggja'], ['hundruð']],
            [[...]]] (1200)

        :param token_verbalizations:
        :return:
        """



        d = self.depth(token_verbalizations)
        if self.max_depth < d:
            self.max_depth = d

        #if len(token_verbalizations) == 1:
        if d == 1:
            if self.paths:
                for p in self.paths:
                    p.append(token_verbalizations)
            else:
                self.paths.append([token_verbalizations])

        elif self.depth(token_verbalizations) == 3:
            self.create_new_paths(len(token_verbalizations))
            for i, elem in enumerate(token_verbalizations):
                for e in elem:
                    if self.paths:
                        self.paths[i].append(e)
                    else:
                        self.paths.append([e])
        else:
            for elem in token_verbalizations:
                if self.paths:
                    for p in self.paths:
                        if isinstance(elem, list):
                            p.append(elem)
                        else:
                            p.append(token_verbalizations)
                else:
                    if isinstance(elem, list):
                        self.paths.append([elem])
                    else:
                        self.paths.append(token_verbalizations)


    def depth(self, verbal_arr):
        if not verbal_arr:
            return 0
        if isinstance(verbal_arr, list):
            return 1 + max(self.depth(item) for item in verbal_arr)
        else:
            return 0

    def create_new_paths(self, new_paths_count):
        """
        Copy paths in self.paths new_paths_count times
        :param new_paths_count:
        :return:
        """
        tmp_paths = self.paths.copy()
        for p in tmp_paths:
            for i in range(new_paths_count-1):
                new_path = p.copy()
                self.paths.append(new_path.copy())



    def print(self):
        for p in self.paths:
            print(str(p))