#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create a frequency dictionary from words in a text.
Options:
--min_occ: only keep those tokens occurring at least min_occ times in the text
--ensure_vocab: ensure the words from a separate word list are included (with freq=0 if not occurring in the input text)

Processes the input text for use in language modeling


"""
import sys
import os
import argparse
import re
import nltk

UNK = '<unk>'

def process_corpus(corpus):
    """
    Processing steps, following Althingi's text norm. corpus preparation (kaldi/egs/althingi/s5/local/make_expansionLM.sh)

    """
    # lowercase
    text = corpus.lower()

    # remove punctuation and other non-alpha numeric symbols
    # only ascii+Icelandic characters kept, is this sufficient?
    text = re.sub('[^a-yáðéíóúýþæö0-9 \n]+', ' ', text)

    # add a space between letters and digits in alphanum tokens

    #text = re.sub('([0-9])([a-záðéíóúýþæö])', '\1 \2' , text)
    #text = re.sub('([a-záðéíóúýþæö])([0-9])', '\1 \2', text)

    # replace digits with '<num>' tag
    text = re.sub('(^|\s)[0-9]+', ' <num>', text)

    # ensure single spaces
    text = re.sub('\s+', ' ', text)

    return text


def extract_wordlist(corpus, min_occ):
    tokens = nltk.tokenize.word_tokenize(corpus)
    fdist = nltk.FreqDist(tokens)
    res_tuples = list(filter(lambda x: x[1] >= min_occ, fdist.items()))
    wordlist = []
    valid_words = set()
    for tup in res_tuples:
        wordlist.append(tup[0] + '\t' + str(tup[1]))
        valid_words.add(tup[0])

    return valid_words, wordlist

def replace_oov(corpus, words):

    oov_replaced = []

    for tok in corpus.split():
        if tok in words:
            oov_replaced.append(tok)
        else:
            oov_replaced.append(UNK)

    return ' '.join(oov_replaced)


def create_word2symbol(words):
    # fix - need more control over tokenizing, such that <num> does not get splitted up
    words.remove('<')
    words.remove('>')
    words.remove('num')
    word2sym = []
    word2sym.append('<eps> 0')
    for i in range(len(words)):
        word2sym.append(words[i] + ' ' + str(i + 1))

    word2sym.append('<unk> ' + str(i + 2))
    word2sym.append('<num> ' + str(i + 3))
    word2sym.append('<word> ' + str(i + 4))

    return word2sym


def print_list(list2write, out_file):

    with open(out_file, 'w') as f:
        for item in list2write:
            f.write(item)
            f.write('\n')


def arguments():
    parser = argparse.ArgumentParser()
                            
    parser.add_argument("infile", type=argparse.FileType('r'))
    parser.add_argument("--min_occ", type=int, default=1, help='min occurrences of a word to be contained in the output')
    parser.add_argument("--ensure_vocab", default='',
                        help='a file containing vocabulary that has to be contained in the word list,'
                                    'regardless of if it is contained in the inputfile or not')

    return parser.parse_args()


def main():
    args = arguments()
    infile = args.infile
    vocab_file = args.ensure_vocab
    min_occ = args.min_occ

    corpus_raw = infile.read()
    clean_corpus = process_corpus(corpus_raw)
    valid_words, wordlist = extract_wordlist(clean_corpus, min_occ)

    clean_corpus_no_oov = replace_oov(clean_corpus, valid_words)

    sym_table = create_word2symbol(sorted(list(valid_words)))
    basename = infile.name[:-4]
    corpus_for_lm = basename + '_for_lm.txt'
    corpus_for_lm_unk = basename + '_for_lm_unk.txt'
    wordlist_for_lm = basename + '_wordlist.txt'
    sym_tab_for_lm = basename + '_word_sym.txt'

    print_list([clean_corpus], corpus_for_lm)
    print_list([clean_corpus_no_oov], corpus_for_lm_unk)
    print_list(wordlist, wordlist_for_lm)
    print_list(sym_table, sym_tab_for_lm)


if __name__ == '__main__':
    main()