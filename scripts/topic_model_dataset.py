# ADAPTED FROM 
# - https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/
# - https://medium.com/swlh/topic-modeling-lda-mallet-implementation-in-python-part-2-602ffb38d396

import argparse
import re
import numpy as np
import pandas as pd
from pprint import pprint
import os.path as osp
import pickle

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess 
from gensim.models import CoherenceModel
from gensim.models.ldamodel import LdaModel

# spacy for lemmatization
import spacy
nlp = spacy.load("en_core_web_sm")

# Plotting tools
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis  # don't skip this
import matplotlib.pyplot as plt

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

# nltk
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
# Some extra words I see a lot
stop_words.extend(['time', 'make', 'find', 'thing', 'know', 'see', 'want', 'think', 'go', 'get'
                   'take', 'tell', 'come', 'say', 'look', 'well', 'much', 'make', 'give', 'let'
                   'ask', 'even', 'call', 'get', 'take', 'feel', 'good', 'go', 'need', 'way', 'say'
                   'let', 'think', 'look', 'keep', 'well' 'else', 'long', 'try', 'still', 'like', 'sure',
                   'many', 'maybe', 'really', 'already', 'put', 'mean', 'suppose', 'right', 'lot',
                   'probably', 'ask', 'use', 'one', 'last', 'ever', 'yet', 'perhaps'])
stop_words = set(stop_words)
from nltk.tokenize import word_tokenize

from hannstats import utils

def _convertldaMalletToldaGen(mallet_model):
    model_gensim = LdaModel(
        id2word=mallet_model.id2word, num_topics=mallet_model.num_topics,
        alpha=mallet_model.alpha) 
    model_gensim.state.sstats[...] = mallet_model.wordtopics
    model_gensim.sync_state()
    return model_gensim

def _path_clean(path):
    if path[:2] == './':
        path = path[2:]
    return path

def _data_loading(datapath):
    df = pd.read_csv(datapath, sep='\t')

    #df['path'] = df['path'].map(lambda x: _path_clean(x))

    #df['path'] = df['path'].map(lambda x: osp.join(text_path, x))

    df['text'] = utils.load_texts(df['path'])

    return df

def _lemmatize(tokens, allowed_postags):
    doc = nlp(" ".join(tokens))
    return [token.lemma_ for token in doc if token.pos_ in allowed_postags]

def _preprocess(df):
    data = df.copy()

    # Tokenize
    data['tokens'] = data['text'].map(lambda x: simple_preprocess(x, deacc=True))

    # Build the bigram models
    bigram = gensim.models.Phrases(data['tokens'], min_count=5, threshold=100) # higher threshold fewer phrases. 
    trigram = gensim.models.Phrases(bigram[data['tokens']], threshold=100)
    # Faster way to get a sentence clubbed as a bigram
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)
    
    # Add bigrams
    data['tokens'] = data['tokens'].map(lambda x: bigram_mod[x])
    data['tokens'] = data['tokens'].map(lambda x: trigram_mod[bigram_mod[x]])

     # Lemmatize
    data['tokens'] = data['tokens'].map(lambda x: _lemmatize(x, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']))

    # Stopword removal
    data['tokens'] = data['tokens'].map(lambda x: [tok for tok in x if tok not in stop_words])

    return data


def _topic_model(df, n_topics, 
                 outpath_data=None, 
                 outpath_viz=None, 
                 pickle_path=None, 
                 mallet_path=None, 
                 alpha=None, 
                 optimize_interval=None,
                 iterations=None):
    # TODO: Topic columns in output dataset should be 1-indexed to match viz

    data = df.copy()

    # Create Dictionary
    id2word = corpora.Dictionary(data['tokens'])

    # Filter out words that occur in less than 10 documents, or more than
    # 50% of documents.
    id2word.filter_extremes(no_below=10, no_above=0.5)

    # Create Corpus
    texts = data['tokens']

    # Term Document Frequency
    corpus = [id2word.doc2bow(text) for text in texts]

    if mallet_path:
        lda_model = gensim.models.wrappers.LdaMallet(mallet_path,
                                                     corpus=corpus, num_topics=n_topics, id2word=id2word,
                                                     alpha=alpha, optimize_interval=optimize_interval,
                                                     iterations=iterations)

        pprint(lda_model.print_topics())

        coherence_model_lda = CoherenceModel(model=lda_model, texts=data['tokens'], dictionary=id2word, coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        print('\nCoherence Score: ', coherence_lda)

        # Get distribution of topics for each topic
        doc_lda = lda_model[corpus]
        print(doc_lda[0])

        corpus_topics = [sorted(topics, key= lambda record: -record[1])[0] for topics in doc_lda]

        # Get most 20 most probable words for given topic
        topics = [[(term, round(wt, 3)) for term, wt in lda_model.show_topic(n, topn=20)] for n in range(0, lda_model.num_topics)]

        # Get a topics dataframe
        topics_df = pd.DataFrame([', '.join([term for term, wt in topic]) for topic in topics], columns = ['Terms per Topic'], index=['Topic'+str(t) for t in range(1, lda_model.num_topics+1)] )

        ldagensim = _convertldaMalletToldaGen(lda_model)
        p = gensimvis.prepare(ldagensim, corpus, id2word, mds='mmds', sort_topics=False)
        
        corpus_topic_df = data.drop(['text', 'tokens'], axis=1)
        #all_topics_frame["Top Topic"] = all_topics_frame.idxmax(axis=1)
        corpus_topic_df['Dominant Topic'] = [item[0]+1 for item in corpus_topics]
        corpus_topic_df['Contribution %'] = [round(item[1]*100, 2) for item in corpus_topics]
        corpus_topic_df['Topic Terms'] = " ".join([topics_df.iloc[t[0]]['Terms per Topic'] for t in corpus_topics][:5])
        corpus_topic_df = pd.concat([corpus_topic_df, pd.DataFrame([[tup[1] for tup in l] for l in doc_lda])], axis=1)

        # Make topic columns 1-indexed
        topic_cols = {t:t+1 for t in range(n_topics)}
        corpus_topic_df = corpus_topic_df.rename(columns=topic_cols)


        # Increase topic numbers by 1 to match the plot
        new_topic_cols = {k:v for k,v in zip([str(x) for x in range(n_topics)], [str(x) for x in range(1,n_topics+1)])}
        corpus_topic_df = corpus_topic_df.rename(new_topic_cols, axis=1)

    else: 
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                               id2word=id2word,
                                               num_topics=n_topics, 
                                               random_state=100,
                                               update_every=1,
                                               chunksize=100,
                                               passes=10,
                                               alpha='auto',
                                               per_word_topics=True)

        pprint(lda_model.print_topics())
        doc_lda = lda_model[corpus]

        # Compute Perplexity
        print('\nPerplexity: ', lda_model.log_perplexity(corpus))  # a measure of how good the model is. lower the better.

        # Compute Coherence Score
        coherence_model_lda = CoherenceModel(model=lda_model, texts=data['tokens'], dictionary=id2word, coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        print('\nCoherence Score: ', coherence_lda)

        all_topics = lda_model.get_document_topics(corpus, minimum_probability=0.0)
        all_topics_csr = gensim.matutils.corpus2csc(all_topics)
        all_topics_numpy = all_topics_csr.T.toarray()
        all_topics_frame = pd.DataFrame(all_topics_numpy)
        all_topics_frame["Dominant Topic"] = all_topics_frame.idxmax(axis=1)+1
        corpus_topic_df = pd.concat([data.drop(['text', 'tokens'], axis=1), all_topics_frame], axis=1)

        topic_cols = {t:t+1 for t in range(n_topics)}
        corpus_topic_df = corpus_topic_df.rename(columns=topic_cols)

        p = gensimvis.prepare(lda_model, corpus, id2word, mds='mmds', sort_topics=False)


    if outpath_data:
        corpus_topic_df.to_csv(outpath_data, sep='\t')

    if outpath_viz:
        pyLDAvis.save_html(p, outpath_viz)

    if pickle_path:
        with open(pickle_path, 'wb') as fp:
            pickle.dump(lda_model, fp)
            
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("datapath", 
                        help="Path to an article-wise dataset. It must have a \
                              column named 'path' storing the path from \
                              text_path to the textfile of each article")
    #parser.add_argument("text_path", help="The path of a folder containing text files of all articles in the dataset")
    parser.add_argument("--outpath_data", \
                        help="Output path for a dataframe \
                              annotated with topic ratios.")

    parser.add_argument("--outpath_viz", 
                         help="Output path for an html page \
                               that visualizes the topics.")

    parser.add_argument("--pickle_path", 
                         help="Output path for a pickle of the model")

    parser.add_argument("--mallet_path", 
                        help="path to a folder with a mallet model. \
                              If included, then will use this to \
                              topic model the data.", 
                        const=None, default=None)
    
    parser.add_argument("-n", 
                        help="number of topics. Default 20.", 
                        nargs='?', type=int, const=20, default=20)

    parser.add_argument("-a", "--alpha", 
                        help="Alpha hparam to pass to Mallet. Default 5.", 
                        nargs='?', type=int, const=5, default=5)

    parser.add_argument("-o", "--optimize_interval", 
                        help="optimize_interval to pass to Mallet. Default 0", 
                        nargs='?', type=int, const=0, default=0)

    parser.add_argument("-i", "--iterations", 
                        help="num_iterations to pass to Mallet. Default 1000.", 
                        nargs='?', type=int, const=1000, default=1000)

    args = parser.parse_args()

    print("Loading Data...")
    df = _data_loading(args.datapath)

    print("Preprocessing...")
    df = _preprocess(df)

    print("Modelling...")
    _topic_model(df, args.n, args.outpath_data, args.outpath_viz, args.pickle_path, 
                mallet_path=args.mallet_path, 
                alpha=args.alpha, 
                optimize_interval=args.optimize_interval, 
                iterations=args.iterations)





if __name__ == "__main__":
    main()
