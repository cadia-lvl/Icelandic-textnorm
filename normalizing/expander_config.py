#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Creates the configuration file needed by text normalization module expander.py

Place your utf8-symbol file, word-symbol file, grammar-fst and language model in one directory
(e.g. 'data/'), change the value sides of this config dictionary according to your filenames.

"""

import configparser

config = configparser.ConfigParser()
config['DATA_DIR'] = {'data': 'data/'}
config['symbol tables'] = {}
config['symbol tables']['utf8'] = 'utf8.syms'
config['symbol tables']['word-symbol'] = 'lm_word_symbol.txt'
config['models'] = {}
config['models']['grammar'] = 'expand_utt_grammar.fst'
config['models']['language model'] = 'gigacorpus_for_lm_unk.fst'

with open('expander.conf', 'w') as configfile:
    config.write(configfile)