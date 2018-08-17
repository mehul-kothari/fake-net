import os
import time
import pickle
import requests
from bs4 import BeautifulSoup


# Libraries for Summary Generation
# We're choosing a plaintext parser here, other parsers available for HTML etc.
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
# We're choosing Lexrank, other algorithms are also built in
from sumy.summarizers.lex_rank import LexRankSummarizer


from newsapi import NewsApiClient
from readability import Document
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
from urllib.parse import urlsplit

import itertools


# Get google trending items nation wise
def get_google_trendings():
	# creating an empty list that we will return
	trending = []
	oldtrends = 'trends.pickle'
	if os.path.exists(oldtrends):
		filetime = os.path.getmtime(oldtrends)
	else:
		filetime = 1900
	trending = []
	if time.time() - filetime > (5 * 60 * 60):
		print("Fetching new trends")
		# pn3 india, pn1 us, pn9 uk
		page = requests.get('http://www.google.com/trends/hottrends/atom/feed?pn=p1')
		doc = page.text
		soup = BeautifulSoup(doc, 'html.parser')
		for topics in soup.find_all("title"):
  			trending.append(topics.text)
		trending.pop(0)
		pickle.dump(trending, open("trends.pickle", "wb"))
	else:
		print("Using old trends")
		trending = pickle.load(open("trends.pickle", "rb"))
	return trending

# This function will generate a summary of a doc with sentences_num sentences


def txt_summary(doc, sentences_num):
    parser = PlaintextParser.from_string(doc, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, sentences_num)
    return summary

# Fetching articles in a multi-threading way


def get_articles(topic):
	# Initializing API
	newsapi = NewsApiClient(api_key='8a77be04382a4f76a3a89e1c9e60c30b')
	top_headlines = newsapi.get_everything(q=topic, language='en', sort_by='relevancy', page_size=20)
   	# Multi-threading document fetching
	pool = Pool(cpu_count() * 2)
	articles = pool.map(fetch_article, top_headlines['articles'])
    # Removing empty articles
	while {} in articles:
		articles.remove({})
	return articles

# helper functions for the above util function
def fetch_article(article):
	try:
		article['source'] = article['source']['name']
		article['surl'] = get_domain(article['url'])
		article['body'] = get_article_body(article['url'])
		if len(article['body']) > 300:
			article['summary'] = txt_summary(article['body'], 5)
		else:
			article = {}
	except Exception as e:
		print(e)
		article = {}
	return article

def fetch_article2(url):
	article = {}
	try:
		article['url'] = url
		article['body'] = get_article_body(url)
		article['summary'] = txt_summary(article['body'], 5)
	except Exception as e:
		print(e)
		article = {}
	return article


def get_domain(url):
	domain = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
	return domain


def get_article_body(url):
	page = requests.get(url, timeout=(3.05, 10))
	doc = Document(page.text)
	soup = BeautifulSoup(doc.summary(), 'html.parser')
	return soup.get_text()



# Multi Document Summary 
def multidoc_summary(articles):
	sentences = []
	for article in articles:
		for sentence in article['summary']:
			sentences.append(sentence)
	summary = ""
	for sent in sentences:
		print(sent)
		summary += " "+str(sent)
	summary = txt_summary(summary, 7)
	return summary

def multidoc_summary2(articles):
	summary = ""
	for article in articles:
		summary += " "+str(article['body'])
	summary = txt_summary(summary, 7)
	return summary


'''
def multidoc_summary(articles):
	sentences = []
	for article in articles:
		for sentence in article['summary']:
			sentences.append(sentence)
	i = 0 
	for pair in itertools.permutations(sentences, 2):
		print(i," : ", pair[0], pair[1])
		i += 1
	print(i)
	summary = str("Summary module is still left, Please try again later")
	return summary
'''