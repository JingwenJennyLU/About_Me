"""
MACS 30121: Analyzing Election Tweets

Jingwen Lu

Analyze module

Functions to analyze tweets. 
"""

import unicodedata
import sys

from basic_algorithms import find_top_k, find_min_count, find_salient

##################### DO NOT MODIFY THIS CODE #####################

def keep_chr(ch):
    '''
    Find all characters that are classifed as punctuation in Unicode
    (except #, @, &) and combine them into a single string.
    '''
    return unicodedata.category(ch).startswith('P') and \
        (ch not in ("#", "@", "&"))

PUNCTUATION = " ".join([chr(i) for i in range(sys.maxunicode)
                        if keep_chr(chr(i))])

# When processing tweets, ignore these words
STOP_WORDS = ["a", "an", "the", "this", "that", "of", "for", "or",
              "and", "on", "to", "be", "if", "we", "you", "in", "is",
              "at", "it", "rt", "mt", "with"]

# When processing tweets, words w/ a prefix that appears in this list
# should be ignored.
STOP_PREFIXES = ("@", "#", "http", "&amp")


#####################  MODIFY THIS CODE #####################


############## Part 2 ##############

def extract_entities_from_tweet(tweet, entity_key, entity_subkey, entity_case):
    '''
    Extract entites from a tweet.

    Inputs:
        tweet: a tweet
        entity_key: the key of an entity
        entity_subkey: the subkey of an entity
        entity_case: the case sensitivity of an entity

    Returns: list of entities
    '''
    entity_lst = []
    for item in tweet['entities'][entity_key]:
        entity = item[entity_subkey]
        if not entity_case:
            entity = entity.lower()
        entity_lst.append(entity)
    return entity_lst


# Task 2.1
def find_top_k_entities(tweets, entity_desc, k):
    '''
    Find the k most frequently occuring entitites.

    Inputs:
        tweets: a list of tweets
        entity_desc: a triple such as ("hashtags", "text", True),
          ("user_mentions", "screen_name", False), etc.
        k: integer

    Returns: list of entities
    '''

    entity_key, entity_subkey, entity_case = entity_desc
    entity_lst = []
    for twt in tweets:
        entity_lst.extend(extract_entities_from_tweet(
            twt, entity_key, entity_subkey, entity_case))
    top_k_entities = find_top_k(entity_lst, k)
    return top_k_entities


# Task 2.2
def find_min_count_entities(tweets, entity_desc, min_count):
    '''
    Find the entitites that occur at least min_count times.

    Inputs:
        tweets: a list of tweets
        entity_desc: a triple such as ("hashtags", "text", True),
          ("user_mentions", "screen_name", False), etc.
        min_count: integer

    Returns: set of entities
    '''

    entity_key, entity_subkey, entity_case = entity_desc
    entity_lst = []
    for twt in tweets:
        entity_lst.extend(extract_entities_from_tweet(
            twt, entity_key, entity_subkey, entity_case))
    return find_min_count(entity_lst, min_count)


############## Part 3 ##############

# Pre-processing step and representing n-grams
def pre_process_clean(tweet, case_sensitive, stopw_sensitive):
    '''
    Pre-process the words

    Inputs:
        tweet(str): a piece of tweet
        case_sensitive (bool): whether is case sensitive
        stopw_sensitive (bool): whether is stop word sensitive

    Return: a list that has done the 6 processes in order
    '''
    tweet_text = tweet['abridged_text']
    lst_tweet = tweet_text.split()
    lst_pure_tweet = []
    for word in lst_tweet:
        stripe_word = word.strip(PUNCTUATION)
        if case_sensitive:
            pure_word = stripe_word
        else:
            pure_word = stripe_word.lower()
        if stopw_sensitive and (stripe_word in STOP_WORDS):
            pure_word = ''
        is_blank = pure_word == ''
        is_prefix = pure_word.startswith(STOP_PREFIXES)
        if (not is_blank) and (not is_prefix):
            lst_pure_tweet.append(pure_word)
    return lst_pure_tweet


def represent_ngram(tweet_lst, n):
    '''
    Compute the n-grams of a tweet

    Inputs:
        tweet_lst (list): a pure list of words in a tweet
        n: the n in n-gram

    Return: a list of tuple of n-gram of the tweet.
    '''

    times = len(tweet_lst) - n + 1
    if times < 1:
        return []
    return [tuple(tweet_lst[i: i + n]) for i in range(times)]



def get_ngram_lst(tweets, case_sensitive, stopw_sensitive, n):
    '''
    Find out all n-grams in all tweets and make them into a list
    while processing the case sensitivity and stop word sensitivity

    Inputs:
        tweets (lst): a list of tweets
        case_sensitive (bool): whether is sensitive to case
        stopw_sensitive (bool): whether is sensitive to stop words
        n (int): n in n-gram
    '''

    all_ngram_lst = []
    for tweet in tweets:
        tweet_lst = pre_process_clean(tweet, case_sensitive, stopw_sensitive)
        n_gram_lst = represent_ngram(tweet_lst, n)
        all_ngram_lst += n_gram_lst
    return all_ngram_lst


# Task 3.1
def find_top_k_ngrams(tweets, n, case_sensitive, k):
    '''
    Find k most frequently occurring n-grams.

    Inputs:
        tweets: a list of tweets
        n: integer
        case_sensitive: boolean
        k: integer

    Returns: list of n-grams
    '''

    all_ngram_lst = get_ngram_lst(tweets, case_sensitive, True, n)
    top_k_ngrams = find_top_k(all_ngram_lst, k)
    return top_k_ngrams


# Task 3.2
def find_min_count_ngrams(tweets, n, case_sensitive, min_count):
    '''
    Find n-grams that occur at least min_count times.

    Inputs:
        tweets: a list of tweets
        n: integer
        case_sensitive: boolean
        min_count: integer

    Returns: set of n-grams
    '''

    all_ngram_lst = get_ngram_lst(tweets, case_sensitive, True, n)
    min_count_ngram = find_min_count(all_ngram_lst, min_count)
    return min_count_ngram


# Task 3.3
def find_salient_ngrams(tweets, n, case_sensitive, threshold):
    '''
    Find the salient n-grams for each tweet.

    Inputs:
        tweets: a list of tweets
        n: integer
        case_sensitive: boolean
        threshold: float

    Returns: list of sets of strings
    '''

    tweets_lst = []
    for tweet in tweets:
        tweet_lst = pre_process_clean(tweet, case_sensitive, False)
        n_gram_lst = represent_ngram(tweet_lst, n)
        tweets_lst.append(n_gram_lst)
    salent_ngram = find_salient(tweets_lst, threshold)
    return salent_ngram
