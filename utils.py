import math
import operator
import os
import pickle
import string

import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer


def tokenize_and_remove_punctuations(s):
    translator = str.maketrans('', '', string.punctuation)
    modified_string = s.translate(translator)
    modified_string = ''.join([i for i in modified_string if not i.isdigit()])
    return nltk.word_tokenize(modified_string)


def stem_words(tokens):
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(token) for token in tokens]
    return stemmed_words


def parse_data(contents):
    contents = contents.lower()
    title_start = contents.find('<title>')
    title_end = contents.find('</title>')
    title = contents[title_start + len('<title>'):title_end]
    text_start = contents.find('<text>')
    text_end = contents.find('</text>')
    text = contents[text_start + len('<text>'):text_end]
    return title + " " + text


def read_data(path):
    contents = []
    for filename in os.listdir(path):
        data = open(path + '/' + filename, 'r').read()
        file_name = filename.replace(".txt", "")
        contents.append((int(file_name), data))
    return contents


def remove_stop_words(tokens):
    stop_words = set(stopwords.words('english'))
    filtered_words = [token for token in tokens if token not in stop_words and len(token) > 2]
    return filtered_words


def get_vocabulary(data):
    tokens = []
    for token_list in data.values():
        tokens = tokens + token_list
    fdist = nltk.FreqDist(tokens)
    return list(fdist.keys())


def preprocess_data(contents):
    dataDict = {}
    for content in contents:
        tokens = tokenize_and_remove_punctuations(content[1])
        filtered_tokens = remove_stop_words(tokens)
        stemmed_tokens = stem_words(filtered_tokens)
        filtered_tokens1 = remove_stop_words(stemmed_tokens)
        dataDict[content[0]] = filtered_tokens1
    return dataDict


def generate_inverted_index(data):
    all_words = get_vocabulary(data)
    index = {}
    for word in all_words:
        for doc, tokens in data.items():
            if word in tokens:
                if word in index.keys():
                    index[word].append(doc)
                else:
                    index[word] = [doc]
    return index


def calculate_tf(tokens):
    tf_score = {}
    for token in tokens:
        tf_score[token] = tokens.count(token)
    return tf_score


def calculate_idf(data):
    idf_score = {}
    N = len(data)
    all_words = get_vocabulary(data)
    for word in all_words:
        word_count = 0
        for token_list in data.values():
            if word in token_list:
                word_count += 1
        idf_score[word] = math.log10(N / word_count)
    return idf_score


def calculate_tfidf(data, idf_score):
    scores = {}
    for key, value in data.items():
        scores[key] = calculate_tf(value)
    for doc, tf_scores in scores.items():
        for token, score in tf_scores.items():
            tf = score
            idf = idf_score[token]
            tf_scores[token] = tf * idf
    return scores


def preprocess_queries(query):
    tokens = tokenize_and_remove_punctuations(query)
    filtered_tokens = remove_stop_words(tokens)
    stemmed_tokens = stem_words(filtered_tokens)
    filtered_tokens1 = remove_stop_words(stemmed_tokens)
    return filtered_tokens1


def calculate_tfidf_queries(query_tokens, idf_score):
    scores = calculate_tf(query_tokens)
    for key, value in scores.items():
        idf = 0
        tf = value
        if key in idf_score.keys():
            idf = idf_score[key]
            scores[key] = tf * idf
    return scores


def rank_results(query, inverted_index, scores, query_scores):
    doc_sim = {}
    for term in query:
        if term in inverted_index.keys():
            docs = inverted_index[term]
            for doc in docs:
                doc_score = scores[doc][term]
                doc_length = math.sqrt(sum(x ** 2 for x in scores[doc].values()))
                query_score = query_scores[term]
                query_length = math.sqrt(sum(x ** 2 for x in query_scores.values()))
                cosine_sim = (doc_score * query_score) / (doc_length * query_length)
                if doc in doc_sim.keys():
                    doc_sim[doc] += cosine_sim
                else:
                    doc_sim[doc] = cosine_sim
    ranked = sorted(doc_sim.items(), key=operator.itemgetter(1), reverse=True)
    return ranked


def get_links_from_ranked_pages(ranked_results, mapping):
    links = []
    for page in ranked_results:
        if page[0] in mapping.keys():
            links.append(mapping[page[0]])
    return links


def extract_mapping(path):
    mapping = {}
    with open(path, 'r') as file:
        for line in file:
            split = line.split(" ")
            mapping[int(split[0])] = split[1]
    return mapping


def get_data_from_pickle(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


def expand_query(query):
    query_tokens = query.split(" ")
    print(query_tokens)
    synonyms = set()
    for token in query_tokens:
        syns = wordnet.synsets(token)
        for syn in syns:
            for l in syn.lemmas():
                synonyms.add(l.name())
    expanded_query = " ".join(x for x in query_tokens + list(synonyms))
    print(expanded_query)
    return expanded_query
