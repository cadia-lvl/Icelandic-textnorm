#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Creates the configuration file needed by text normalization module normalizer.py

Place your utf8-symbol file, word-symbol file, grammar-fst and language model in one directory
(e.g. 'data/'), change the value sides of this config dictionary according to your filenames.

"""

import configparser

config = configparser.ConfigParser()
config['DATA_DIR'] = {'data': 'data/'}
config['symbol tables'] = {}
config['symbol tables']['utf8'] = 'utf8.syms'
config['symbol tables']['word-symbol'] = 'mixed_word_sym.txt'
config['models'] = {}
config['models']['language model'] = 'TRAINING_MIXED_for_lm_unk.fst'
config['thrax'] = {'thrax': 'thrax_grammar/'}
config['thrax grammars'] = {}
config['thrax grammars']['classifier grammar'] = 'classify/TOKENIZE_AND_CLASSIFY'
config['thrax grammars']['verbalizer grammar'] = 'verbalize_tags/ALL'

with open('normalizer.conf', 'w') as configfile:
    config.write(configfile)