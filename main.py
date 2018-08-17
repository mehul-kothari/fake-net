from flask import Flask, render_template, request, redirect, url_for, jsonify
import os, pickle
from operator import itemgetter
from utils import get_google_trendings, txt_summary, get_articles, multidoc_summary, fetch_article2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
import numpy as np
import json

model = pickle.load(open("model.pickle", "rb"))
vectorizer = pickle.load(open("vectorize.pickle", "rb"))


app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/', methods=['GET'])
def index():
  trending = get_google_trendings() # utils
  topic = str("")
  if(request.args != {}):
      topic = str(request.args.get('query'))
      articles = get_articles(request.args.get('query'))
      articles = articles_check(articles)
      summary = multidoc_summary(articles[:3])
  else:
    articles = []
    summary = []
  return render_template('index.html', trends= trending,articles = articles, summary = summary, topic = topic)


@app.route('/fake_check', methods=['GET'])
def fake_check():
    article = {}
    if(request.args != {}):
        url = str(request.args.get('url'))
        article = fetch_article2(url)
        print(article)
        article['true'], article['false'] = article_check(url)
    return render_template('fake_check.html', article = article)

@app.route('/fake_api',methods = ['GET', 'POST', 'DELETE'])
def fake_api():
    if request.method == 'POST':
        mystr = request.json["txt"]
        true,false = article_check(mystr)
    return jsonify(fake=false, true=true)

@app.route('/shutdown', methods=['GET'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'
    
def articles_check(articles):
    for article in articles:
        X = vectorizer.transform([article['body']])
        article['score'] = round(model.predict_proba(X)[0][0] * 100,2);
    articles = sorted(articles, key=itemgetter('score'), reverse=True)
    return articles

def article_check(body):
    X = vectorizer.transform([body])
    y = model.predict_proba(X)
    print(y)
    return round(y[0][0] * 100, 2) , round(y[0][1] * 100, 2)



@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
