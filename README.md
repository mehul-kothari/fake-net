# Fake News Net

A web application built on Flask to determine credibility of news.
It uses a binary classifier which detects whether a news article is credible or not.


## Getting Started

Install all the libraries from requirements.txt

```
pip install -r requirements.txt
```

### Prerequisites

1. Install Python 3.6+.
2. Install all dependencies.
3. Download NLTK data which it asks you to download.

### Installing

Start the flask application by

```
python main.py
```



### Retrain model 

1. Add more data to train.py  

2. Run the generate_model python script

```
python model\generate_model.py
```

3. Copy the pickle files from the model to root folder.

## Deployment

1. Use a proper web server like gunicorn.
2. Min specs for the server
   - 1 CPU
   - 2+ GB RAM (due to large tfidf vector)
   - 1+ GB Disk Space
   - 5 mbps + Internet Connectivity
