#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pynini as pn


SPACE = '0x0020'

class TransitionGraph:

    def __init__(self, utf8_symbols):
        self.transitions = {}
        self.utf8_symbols = utf8_symbols


    def extract_verbalization(self, verbalized_fst):
        """
        Create a transitions graph from the verbalized_fst and extract all possible verbalizations
        :param verbalized_fst:
        :param utf8_symbols:
        :return:
        """
        self._init_transitions_graph(verbalized_fst)
        paths = self._find_all_paths(self.transitions, 0, verbalized_fst.num_states())
        verbalizations = self._extract_words_from_paths(paths)
        return verbalizations


    def _init_transitions_graph(self, inp_fst):

        final_state = self._find_final_state(inp_fst)
        # set the first transition state
        self._set_transitions_from_state(inp_fst, inp_fst.start(), final_state)
        num_states = inp_fst.num_states()

        for i in range(inp_fst.start(), num_states):
            # set all following transitions
            if i == inp_fst.start():
                continue
            self._set_transitions_from_state(inp_fst, i, final_state)


    def _set_transitions_from_state(self, inp_fst, current, final_state):

        # TODO: need this?
        #if current < 0:
            # somehow an empty fst got here
        #    return

        arc_it = inp_fst.arcs(current)
        current_weight = inp_fst.final(current)

        if current_weight != pn.Weight.Zero(current_weight.type()):
            # we are in a potential final state, if it is not the absolute final state,
            # construct an empty path from the current state (start) to the absolute final state,
            # otherwise we cant't extract the path later that ends here.
            if final_state != current:
                self.transitions[current] = [(final_state, '')]

        # extract all outgoing arcs from current state with output labels
        while not arc_it.done():
            val = arc_it.value()
            next_state = val.nextstate
            label = self.utf8_symbols.find(val.olabel).decode('utf-8')
            if current in self.transitions:
                self.transitions[current].append((next_state, label))
            else:
                self.transitions[current] = [(next_state, label)]
            arc_it.next()

    def _find_final_state(self, inp_fst):
        # sometimes the highest numbered state is not the final state - or not a possible final state at all
        # we don't wan't the default final arc leading to that state, but to the real final state
        # Example: path is: ... 21, 23 [possible final], 24, 22 [absolute final]
        # Final state has a weight != Weight.Zero and its arc_iterator is done.

        final_state = inp_fst.num_states() - 1

        while final_state > 0:
            state_weight = inp_fst.final(final_state)
            arc_it = inp_fst.arcs(final_state)
            if state_weight != pn.Weight.Zero(state_weight.type()) and arc_it.done():
                return final_state

            final_state -= 1

        return final_state

    def _find_all_paths(self, graph, start, end, path=[]):
        """
        Finds all paths through 'graph'.
        See: https://www.python.org/doc/essays/graphs/

        :param graph:
        :param start:
        :param end:
        :param path:
        :return:
        """
        path = path + [start]
        if start == end:
            return [path]
        if start not in graph:
            return [path]
        paths = []
        for node in graph[start]:
            if node[0] not in path and node[0] != 0:
                newpaths = self._find_all_paths(graph, node[0], end, path)
                for newpath in newpaths:
                    paths.append(newpath)

        return paths

    def _extract_words_from_paths(self, paths):

        words = []
        for path in paths:
            w = ''
            for i, elem in enumerate(path):
                if i < len(path) - 1:
                    label_arr = self._sort_tuples(self.transitions[elem])

                    if len(label_arr) > 1 and self._contains_same_transition(label_arr):
                        # deal with same source-dest state with different arcs (e.g. fyrsti, fyrsta, fyrstu)
                        for tup in label_arr:
                            current_tup = tup
                            if current_tup[0] == path[i + 1]:
                                w = self._add_to_word(current_tup, w)
                                if self._has_same_state(current_tup, label_arr):
                                    self._remove_tupel(current_tup, self.transitions, elem)
                                break
                    else:
                        for tup in label_arr:
                            if tup[0] == path[i + 1]:
                                w = self._add_to_word(tup, w)

            words.append(w)

        return words

    def _sort_tuples(self, tuple_arr):
        # TODO: util?
        return sorted(tuple_arr, key=lambda x: x[0])

    def _contains_same_transition(self, label_arr):
        # if the number of destination states is smaller than the length of label_arr
        # then we have at least one duplicated transition

        dest_states = set()
        for tup in label_arr:
            dest_states.add(tup[0])

        if len(dest_states) < len(label_arr):
            return True

        return False

    def _add_to_word(self, tup, w):

        if tup[1] == SPACE:
            w = w + ' '
        else:
            w = w + tup[1]

        return w

    def _has_same_state(self, current_tup, tuple_arr):
        # TODO: util?
        ref_state = current_tup[0]
        counter = 0
        for tup in tuple_arr:
            if tup[0] == ref_state:
                counter += 1
        if counter > 1:
            return True

        return False

    def _remove_tupel(self, tupel, tuple_dict, elem):
        #TODO: util?
        arr = tuple_dict[elem]
        arr.remove(tupel)
        tuple_dict[elem] = arr








