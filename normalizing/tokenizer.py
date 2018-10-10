
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize


class Tokenizer:

    def tokenize_sentence(self, text):
        sentence_list = sent_tokenize(text)
        return sentence_list

    def tokenize_words(self, sentence):
        word_list = word_tokenize(sentence)
        return word_list


def main():
    tok = Tokenizer()

    s_list = tok.tokenize_sentence("Tíu árum eftir hrun vita Björn Arnarson og Halla Sigrún Gylfadóttir, hjón með tvö "
                                   "börn í hálfkláruðu húsi, loksins hvað þau skulda Arion banka. Af þessum 240 atriðum "
                                   "eru yfir 150 íslensk bönd en hátíðin fer fram 7.-10. nóvember. Draumur þeirra að "
                                   "byggja fallegt hús við Elliðavatn í Kópavogi varð að martröð við fall bankanna í "
                                   "október 2008. Björn og Halla voru á meðal þeirra sem sögðu sögu sína í "
                                   "heimildarmyndinni Nýja Ísland sem sýnd var á Stöð 2 í vikunni.")
    w_list = tok.tokenize_words(s_list[2])

    print(' '.join(w_list))

    for elem in w_list:
        print(elem)

if __name__=='__main__':
    main()