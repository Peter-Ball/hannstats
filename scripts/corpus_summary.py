'''
Generate corpus-wide summary statistics.
- Sentence length
- Word and bi-gram frequency
- topic modelling
'''

import argparse
import os,re
import nltk
from nltk.tokenize import RegexpTokenizer, sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter
from nltk.util import ngrams
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')


def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus_path", 
                        help="directory with text files that make up the corpus"
                        )
    args = parser.parse_args()

    texts = []
    for doc in os.listdir(args.corpus_path):
        if doc[-4:] == '.txt':
            path = os.path.join(args.corpus_path, doc)
            with open(path) as fp:
                texts.append(fp.read().decode('utf-8'))

    # Average sentnece length
    sents = [sent for sentlist in [sent_tokenize(text) for text in texts] for sent in sentlist]
    sent_lens = [len(s) for s in sents]
    avg_sent_len = sum(sent_lens)/len(sent_lens)
    print("Average sentence length: {}".format(avg_sent_len))

    # First, preprocess
    ## extend stopwords
    stopwords = set(nltk.corpus.stopwords.words('english'))
    extra_sw = set(['could', 'one', 'would', 'said', 'like', 'got', 'get'])
    stopwords = stopwords.union(extra_sw)
    ## word tokenize
    tokenizer = RegexpTokenizer(r'\w+')
    lem = WordNetLemmatizer()
    words = [word for wordlist in [tokenizer.tokenize(text.lower()) for text in texts] for word in wordlist]

    ## remove stopwords
    words = [word for word in words if word not in stopwords]
    ## Lemmatize
    words = [lem.lemmatize(word) for word in words if len(word) > 2]

    # get wordcounts
    word_counts = Counter(words)
    top_10 = word_counts.most_common(10)
    top_10_words = [word for word,count in top_10]

    ##Output
    print("Top 10 words:\n{}".format(' '.join(top_10_words).encode('utf-8')))

    # Get NGrams
    bigram_counts = Counter(list(ngrams(words, 2)))
    top_10_bigrams = ['({0} {1})'.format(bg[0], bg[1]) for bg,count in bigram_counts.most_common(10)]

    ##Output
    print("top 10 bigrams:\n{}".format(' '.join(top_10_bigrams).encode('utf-8')))




if __name__ == "__main__":
    main()