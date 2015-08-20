import itertools
from operator import itemgetter
from math import sqrt
from collections import Counter
import math

from networkx import Graph, pagerank
from nltk import tokenize

from ml_util import cachedStopWords, strip_signature


def summarize_email(raw_text, sender=None,  language='english'):
    raw_text = strip_signature(raw_text, sender)
    stopwords = cachedStopWords
    sentence_list = tokenize.sent_tokenize(raw_text, language)
    word_set = [get_tokenized(sentence, stopwords) for sentence in sentence_list]

    graph = Graph()
    pairs = itertools.combinations(enumerate(filter(None, word_set)), 2)
    for (index_a, words_a), (index_b, words_b) in pairs:
        similarity = cosine(words_a, words_b)
        if similarity > 0:
            graph.add_edge(index_a, index_b, weight=similarity)

    if not graph.edges():
        return sentence_list[0]

    ranked_sentence_indexes = pagerank(graph).items()
    sentences_by_rank = sorted(ranked_sentence_indexes, key=itemgetter(1), reverse=True)
    summary_size = int(math.ceil(len(sentence_list) / 3))
    best_sentences = map(itemgetter(0), sentences_by_rank[:summary_size])
    best_sentences_in_order = sorted(best_sentences)
    return ' '.join(sentence_list[index] for index in best_sentences_in_order)


def cosine(words_a, words_b):
    words_a, words_b = Counter(words_a), Counter(words_b)
    intersection = set(words_a.keys()) & set(words_b.keys())
    numerator = sum([words_a[x] * words_b[x] for x in intersection])

    words_a_sum = sum([words_a[x] ** 2 for x in words_a.keys()])
    words_b_sum = sum([words_b[x] ** 2 for x in words_b.keys()])
    denominator = sqrt(words_a_sum) * sqrt(words_b_sum)

    return 0.0 if not denominator else float(numerator) / denominator


def get_tokenized(sentence, stopwords):
    return set(word for word in tokenize.word_tokenize(sentence) if word.isalnum() and word not in stopwords)
