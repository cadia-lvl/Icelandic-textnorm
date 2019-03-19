#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stores all different verbalizing options for an utterance.

"""

class Verbalized:

    def __init__(self):
        self.paths = []
        self.max_depth = 0

    def __str__(self):
        return str(self.paths)


    def extend_paths(self, token_verbalizations):
        """
        Extends paths with the token verbalizations that can be:
        a) an array of depth 1, with only one word in the containing array (non-ambiguous verbalization/token type WORD)
        b) an array of depth 3 >= 1, where at least one of the arrays has more than one entries
        c) an array of depth 3 containing a list of arrays, for non-compatible verbalization paths

        a) ['fimm'] (5)
        b) [['tuttugu'],['og'],['tvo', 'tvær', 'tveir', 'tveimur', 'tveggja']] (22)
        c) [[['tólf'], ['hundruð']],
            [['eitt'], ['þúsund'], ['og'], ['tvo', 'tvær', 'tveir', 'tveimur', 'tveggja'], ['hundruð']],
            [[...]]] (1200)

        :param token_verbalizations:
        :return:
        """

        list_depth = self._depth(token_verbalizations)
        if self.max_depth < list_depth:
            self.max_depth = list_depth

        if list_depth == 1:
            if self.paths:
                for p in self.paths:
                    p.append(token_verbalizations)
                    #p.append(' '.join(token_verbalizations))
            else:
                self.paths.append([token_verbalizations])
                #self.paths.append([' '.join(token_verbalizations)])

        elif list_depth == 3:
            # need to copy existing paths, once for each 2nd level list in token_verbalization
            self._create_new_paths(len(token_verbalizations))
            self._update_deep_paths(token_verbalizations)
        else:
            self._update_paths(token_verbalizations)

    #
    #  PRIVATE METHODS
    #

    def _update_paths(self, token_verbalizations):
        self.paths.sort()
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

    def _update_deep_paths(self, token_verbalizations):
        self.paths.sort()
        for i, elem in enumerate(token_verbalizations):
            if self.paths:
                for j in range(i, len(self.paths), len(token_verbalizations)):
                    for e in elem:
                #if self.paths:
                        self.paths[j].append(e)
            else:
                self.paths.append([e])


    def _create_new_paths(self, new_paths_count):
        """
        Copy paths in self.paths new_paths_count times
        :param new_paths_count:
        :return:
        """
        tmp_paths = self.paths.copy()
        if tmp_paths:
            for p in tmp_paths:
                for i in range(new_paths_count-1):
                    new_path = p.copy()
                    self.paths.append(new_path.copy())
        else:
            for i in range(new_paths_count):
                self.paths.append([])


    def _depth(self, verbal_arr):
        # TODO: util?
        if not verbal_arr:
            return 0
        if isinstance(verbal_arr, list):
            return 1 + max(self._depth(item) for item in verbal_arr)
        else:
            return 0


