import argparse
import os
import random
import numpy as np


class NGramModel:

    def __init__(self, N=2):
        '''
        length of the gram
        smoothing
        '''

        self.N = N


    def generate_features(self, file_path):
        '''
        commenting
        '''

        f = open(file_path)
        text = f.read()

        # edit text
        text = text.lower().replace('\n', ' ').replace('(', '').replace(')', '')\
                    .replace('"', '').replace("'", '').replace(',', '').replace(';', '')\
                    .replace(':', '').replace('!', '.').replace('?', '.').strip()

        # create list with sequences, remove white space
        textlist = text.split(sep='.')
        if '' in textlist:
            textlist.remove('')
        for k in range(len(textlist)):
            textlist[k] = textlist[k].strip()

        # create list of words from sentence and add start and stop codon
        start = ['<s>'] * (self.N-1)
        end = ['</s>'] * (self.N-1)
        for k in range(len(textlist)):
            sen = textlist[k]
            sen = sen.split(sep=' ')
            textlist[k] = start + sen + end

        # remove sequences if they are too short
        for sen in textlist:
            if len(sen) < 1+(self.N-1)*3:
                textlist.remove(sen)

        # create vocabulary
        unique_words = set(text.replace('.', '').split(sep=' '))
        unique_words = sorted(unique_words)
        vocabulary = {}
        for word in unique_words:
            word = word.strip()
            if len(word) > 0:
                vocabulary[word] = text.count(word)
        # add start and stop count manually
        vocabulary['<s>'] = len(textlist)
        vocabulary['</s>'] = len(textlist)


        return vocabulary, textlist


    def generate_probability(self, vocabulary, textlist):
        '''
        commenting
        '''

        probdict = {}
        # count words
        for seq in textlist:
            for n in range(len(seq)-(self.N-1)):
                if not seq[n] in probdict:
                    probdict[seq[n]] = {}

                if not seq[n+1] in probdict[seq[n]]:
                    probdict[seq[n]][seq[n+1]] = 0

                probdict[seq[n]][seq[n+1]] += 1

        # normalize to log probability
        for key, dic in probdict.items():
            countSum = vocabulary[key]
            for word, count in dic.items():
                try:
                    count = int(count)
                except ValueError:
                    print(word, count)
                    import ipdb; ipdb.set_trace()

                dic[word] = np.log(count/countSum)

        return probdict


    def generate_text(self, probdict, nseq=1):
        '''
        commenting
        '''

        text = []
        for n in range(nseq):
            sequence = ['<s>']
            while '</s>' not in sequence[-1]:
                last = sequence[-1]
                opts = list(probdict[last].keys())
                weights = np.exp(list(probdict[last].values()))
                nextword = random.choices(opts, weights=weights)
                sequence += nextword

            sequence = sequence[(self.N-1):-(self.N-1)]
            sequence = ' '.join(sequence)
            sequence = sequence + '.'
            text.append(sequence)

        text = ' '.join(text)

        return text

def main():
    #ArgumentParser
    parser = argparse.ArgumentParser(description='Generate n-gram model')
    parser.add_argument('-lg', help='length of gram', type=int)
    parser.add_argument('-lt', help='umber of sentences', type=int)
    parser.add_argument('-td','--text_dir', help='text directory path', type=str)
    args = vars(parser.parse_args())

    length = args['lg']
    nseq = args['lt']
    text_dir = args['text_dir']

    # N = length of sequence
    NG = NGramModel(N=length)

    vocabulary, textlist = NG.generate_features(text_dir)
    probability = NG.generate_probability(vocabulary, textlist)
    text = NG.generate_text(probability, nseq=nseq)

    print(text)


if __name__ == '__main__':
    main()

