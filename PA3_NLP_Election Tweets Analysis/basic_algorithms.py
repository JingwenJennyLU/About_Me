"""
MACS 30121: Analyzing Election Tweets

Jingwen Lu

Basic algorithms module

Algorithms for efficiently counting and sorting distinct 'entities',
or unique values, are widely used in data analysis.
"""

import math
from util import sort_count_pairs


# Task 1.1
def count_tokens(tokens):
    '''
    Counts each distinct token (entity) in a list of tokens.

    Inputs:
        tokens: list of tokens (must be immutable)

    Returns: dictionary that maps tokens to counts
    '''

    count_dic = {}
    for tk in tokens:
        count_dic[tk] = count_dic.get(tk, 0) + 1
    return count_dic


# Task 1.2
def find_top_k(tokens, k):
    '''
    Find the k most frequently occuring tokens.

    Inputs:
        tokens: list of tokens (must be immutable)
        k: a non-negative integer

    Returns: list of the top k tokens ordered by count.
    '''

    if k < 0:
        raise ValueError("In find_top_k, k must be a non-negative integer")

    if k == 0:
        return []

    counted_dic = count_tokens(tokens)

    pairs = list(counted_dic.items())
    sorted_pairs = sort_count_pairs(pairs)

    return [token for token, count in sorted_pairs[:k]]


# Task 1.3
def find_min_count(tokens, min_count):
    '''
    Find the tokens that occur *at least* min_count times.

    Inputs:
        tokens: a list of tokens  (must be immutable)
        min_count: a non-negative integer

    Returns: set of tokens
    '''

    if min_count < 0:
        raise ValueError("min_count must be a non-negative integer")

    counted_dic = count_tokens(tokens)
    return_set = set()
    for key, value in counted_dic.items():
        if value >= min_count:
            return_set.add(key)

    return return_set


# Task 1.4
def cal_tf(docs_max_freq, term, counted_token):
    '''
    Compute the augmented frequency of the term t in a document d.

    Inputs:
        docs_max_freq (int): the maximum number of times that any term
            appears in document d;
        term (str): term t;
        counted_token (dictionary) = dictionary that maps the token
            to frequency in document d

    Return:
        tf (float): the augmented frequency of the term t in d.
    '''

    freq_t = counted_token[term]
    tf = 0.5 + 0.5 * (freq_t / docs_max_freq)
    return tf


def find_salient(docs, threshold):
    '''
    Compute the salient words for each document.  A word is salient if
    its tf-idf score is strictly above a given threshold.

    Inputs:
      docs: list of list of tokens
      threshold: float

    Returns: list of sets of salient words
    '''

    num_docs = len(docs)
    df_dic = {}
    counted_lst = []
    for doc in docs:
        counted = count_tokens(doc)
        counted_lst.append(counted)
        for term in counted.keys():
            df_dic[term] = df_dic.get(term, 0) + 1

    idf_dic = {term: math.log(num_docs / df) for term, df in df_dic.items()}
    salient_lst = []

    for doc_i, doc in enumerate(docs):
        salient_terms = set()
        if len(doc) != 0:
            counted_token = counted_lst[doc_i]
            doc_max_freq = max(counted_token.values())

            for term in counted_token:
                tf = cal_tf(doc_max_freq, term, counted_token)
                tf_idf = tf * idf_dic[term]
                if tf_idf > threshold:
                    salient_terms.add(term)
        salient_lst.append(salient_terms)
    return salient_lst
