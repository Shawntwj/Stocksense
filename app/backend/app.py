# remember to pip install:
    # flask
    # git+https://github.com/JustAnotherArchivist/snscrape.git
    # GoogleNews
    # newspaper3k
    # flair
    # happytransformer
    # psaw
    # flask_cors
    # pandas_datareader
    # pmdarima
    # statsmodels

import time
import datetime
from flask import Flask
from flask import jsonify
from flask_cors import CORS
import pandas as pd
import statistics

# libraries for Stocktwits
import requests
import json
import os

# libraries for News
from GoogleNews import GoogleNews
from newspaper import Article
from newspaper import Config

# libraries for Twitter
import snscrape.modules.twitter as sntwitter

# libraries for Reddit
from psaw import PushshiftAPI

# libraries for clean
import re
import nltk
from nltk import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import numpy as np

# libraries for sentiment analysis
import flair
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from happytransformer import HappyTextClassification

# libraries for prediction
from pandas_datareader import data
from sklearn.metrics import mean_squared_error
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA


app = Flask(__name__)
CORS(app)

@app.route('/')
def healthCheck():
    return 200

# Stocktwits scraper
def first_check(symbol):
    url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json?filter=top&limit=20"
    req = requests.get(url)
    data_dict = req.json()
    if data_dict["response"]["status"] == 200:
        return True
    return False

@app.route('/api/stocktwits/<string:symbol>/<string:senti_type>/')
def getStocktwits(symbol, senti_type):
    if (first_check(symbol)):
        data = []

        # end_date = datetime.datetime.today()

        # start_date = (end_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        # start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        # end_date = datetime.datetime.strptime(end_date.strftime('%Y-%m-%d'), "%Y-%m-%d")
        start_date = datetime.datetime.now()
        end_date = start_date - datetime.timedelta(days=1)

        j = 0   # page number
        postid = ''

        while start_date >= end_date:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json?filter=top&limit=40"

            if j > 0:
                url += postid

            req = requests.get(url)
            data_dict = req.json()

            if data_dict["response"]["status"] == 200:
                main_body = data_dict["messages"]
                for i in range(len(main_body)):
                    person_id_data = main_body[i]["id"]
                    content_data = main_body[i]["body"]

                    content_data = content_data.replace("’", "'")
                    content_data = content_data.replace("&#39;","'")

                    time = main_body[i]["created_at"]
                    timelist = time.split("T")

                    date_created_data = timelist[0]

                    start_date = datetime.datetime.strptime(date_created_data, "%Y-%m-%d")

                    # if (start_date == end_date):

                    time_created_data = timelist[1][:-1]

                    username_data = main_body[i]["user"]["username"]
                    name_data = main_body[i]["user"]["name"]
                    join_date_data = main_body[i]["user"]["join_date"]
                    official_data = main_body[i]["user"]["official"]
                    followers_data = main_body[i]["user"]["followers"]
                    source_data =  main_body[i]["source"]["title"]
                    try:
                        likes_data =  main_body[i]["likes"]["total"]
                    except:
                        likes_data = 0

                    postid = data_dict["cursor"]["max"]
                    postid = "&max=" + str(postid)

                    data.append({
                        "person_id": person_id_data,
                        "content": content_data,
                        "date_created": date_created_data,
                        "time_created": time_created_data,
                        "username": username_data,
                        "name": name_data,
                        "join_date": join_date_data,
                        "official": official_data,
                        "followers": followers_data,
                        "source": source_data,
                        "likes": likes_data
                    })

            j += 1

        return getResponse(data, senti_type)

# News scraper
def getArticleSummary(parsed_news, start_date):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    config = Config()
    config.browser_user_agent = user_agent

    data=[]
    for ind in parsed_news:
        dicti={}
        article = Article(ind[1],config=config)
        try:
            article.download()
            article.parse()
            article.nlp()

            dicti['title']=article.title
            dicti['content']=article.text
            dicti['summary']=article.summary
            dicti['link']=ind[1]
            if article.publish_date == None:
                dicti['date']=start_date
            else:
                dicti['date']=article.publish_date

            data.append(dicti)
        except:
            pass

    return data

def getGoogleNewsLinks(symbol, start_date):
    parsed_news = []

    end_date = (start_date - datetime.timedelta(days=1)).strftime('%m/%d/%Y')
    start_date = start_date.strftime('%m/%d/%Y')

    googlenews=GoogleNews(start = end_date, end = start_date) #month/day/year
    googlenews.search(symbol)

    for i in range(2, 20):
        googlenews.getpage(i)
        result=googlenews.result()
        df=pd.DataFrame(result)

    for ind in df.index:
        link = df['link'][ind]
        parsed_news.append([symbol, link])

    return parsed_news

@app.route('/api/news/<string:symbol>/<string:senti_type>/')
def getNews(symbol, senti_type):
    start_date = datetime.datetime.now()
    parsed_news = getGoogleNewsLinks(symbol, start_date)
    data = getArticleSummary(parsed_news, start_date)
    return getResponse(data, senti_type)

# Twitter scraper
@app.route('/api/twitter/<string:symbol>/<string:senti_type>/')
def getTwitter(symbol, senti_type):
    """
    Using TwitterSearchScraper to scrape data and append tweets to list
    - assumes date format to be YYYY-MM-DD
    - end date exclusive for twitter
    - with conditions: min word length = 5, min like = 200, min followers = 50, min retweet = 5
    """
    data = []
    end_date = datetime.datetime.today()
    start_date = (end_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    items = sntwitter.TwitterSearchScraper(f"{symbol} since:{start_date} until:{end_date}").get_items()
    for i,tweet in enumerate(items):
        if len(tweet.content.split())>=5 and tweet.likeCount>=200 and tweet.user.followersCount>=50 and tweet.retweetCount>=5:
            data.append({
                "username": tweet.user.username,
                "content": tweet.content,
                "datetime": tweet.date,
                "followers": tweet.user.followersCount,
                "comments": tweet.replyCount,
                "shares": tweet.retweetCount,
                "likes": tweet.likeCount
            })

    return getResponse(data, senti_type)

# Reddit scraper
def reddit_sentiment_comment(search, start, end, subreddit):
    api = PushshiftAPI()

    s = datetime.datetime.strptime(start, '%d/%m/%Y')
    e = datetime.datetime.strptime(end, '%d/%m/%Y')
    start_date = time.mktime(datetime.datetime.strptime(start, "%d/%m/%Y").timetuple())
    end_date = time.mktime(datetime.datetime.strptime(end, "%d/%m/%Y").timetuple())
    comments = []

    S = api.search_comments(subreddit=subreddit, after=s, before=e)  # Pull posts within date range
    for comment in S:  # Looping through each post
        try: # Try/except to catch any erroneous post pulls
            if comment.body != '[removed]' and comment.body != '[deleted]' and search[0] in comment.body or search[1] in comment.body or search[2] in comment.body or search[3] in comment.body or search[4] in comment.body: # Remove the deleted posts
                comments.append({
                    'content':comment.body,
                    'username':comment.author_fullname,
                    'score':comment.score,
                    'comment_id':comment.id,
                    'subreddit':comment.subreddit,
                    'parent_id':comment.parent_id,
                    'created':datetime.datetime.fromtimestamp(comment.created)
                })  # Retrieve post data and append to dataframe
        except:
            continue # Continue loop if error is found

    return comments

def reddit_sentiment_post(search, start, end, subreddit):
    api = PushshiftAPI()
    s = datetime.datetime.strptime(start, '%d/%m/%Y')
    e = datetime.datetime.strptime(end, '%d/%m/%Y')
    start_date = time.mktime(datetime.datetime.strptime(start, "%d/%m/%Y").timetuple())
    end_date = time.mktime(datetime.datetime.strptime(end, "%d/%m/%Y").timetuple())
    posts = []

    S = api.search_submissions(subreddit=subreddit, after=s, before=e) # Pull posts within date range

    for post in S:  # Looping through each post
        try: # Try/except to catch any erroneous post pulls
            if post.title != '[removed]' and post.title != '[deleted]'and search[0] in post.title or search[1] in post.title or search[2] in post.title or search[3] in post.title or search[4] in post.title:
                posts.append({
                    'title':post.title,
                    'score':post.score,
                    'upvote_ratio':post.upvote_ratio,
                    'id':post.id,
                    'subreddit':post.subreddit,
                    'url':post.url,
                    'num_comments':post.num_comments,
                    'content':post.selftext,
                    'created':datetime.datetime.fromtimestamp(post.created)
                })  # Retrieve post data and append to dataframe
        except:
            continue # Continue loop if error is found

    return posts

def getReddit(redditType, symbol, senti_type):
    today = datetime.datetime.today()
    start_date = (today - datetime.timedelta(days=1)).strftime('%d/%m/%Y')
    end_date = (today + datetime.timedelta(days=1)).strftime('%d/%m/%Y')
    # """convert date format to %d/%m/%Y"""
    # start = "/".join(start_date.split("-")[::-1])
    # end = (datetime.datetime.strptime(start, "%d/%m/%Y") + datetime.timedelta(days=1)).strftime("%d/%m/%Y")
    sub = "stocks"
    if redditType == "comment":
        data = reddit_sentiment_comment(symbol, start_date, end_date, sub)
    elif  redditType == "post":
        data = reddit_sentiment_post(symbol, start_date, end_date, sub)
    return getResponse(data, senti_type)

@app.route('/api/reddit:comment/<string:symbol>/<string:senti_type>/')
def getRedditComments(symbol, senti_type):
    return getReddit("comment", symbol, senti_type)

@app.route('/api/reddit:post/<string:symbol>/<string:senti_type>/')
def getRedditPosts(symbol, senti_type):
    return getReddit("post", symbol, senti_type)

# Clean
def getCleanedContent(data):
    cleaned_data = []
    for item in data:
        item["content"] = item["content"].lower()
        item["content"] = remove_hashtag_mentions_urls(item["content"])
        item["content"] = remove_emoji(item["content"])
        item["content"] = tokenization(item["content"])
        item["content"] = ' '.join(item["content"])
        cleaned_data.append(item)
    return cleaned_data

def remove_hashtag_mentions_urls(text):
    return re.sub(r"(?:\@|\#|https?\://)\S+", "", text)

def remove_emoji(text):
    emoji_pattern = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def tokenization(text):
    word_tokenizer = RegexpTokenizer(r'[-\'\w]+')
    tokenized_text = word_tokenizer.tokenize(text)
    return tokenized_text

# Sentiment
def flair_sentiment(data):
    flair_sentiment = flair.models.TextClassifier.load('en-sentiment')  # Load model
    if len(data) == 0:
        return data
    for row in data:
        s = flair.data.Sentence(row["content"])
        flair_sentiment.predict(s)
        sentiment = str(s.labels[0]).split()[0]
        score = str(s.labels[0]).split()[1][1:-1]

        row["sentiment"] = sentiment
        row["score"] = score
    return data

def vader_sentiment(data):
    sia = SentimentIntensityAnalyzer()  # Load model
    if len(data) == 0:
        return data
    for row in data:
        vs = sia.polarity_scores(row["content"])
        score = vs["compound"]
        del vs['compound']
        sentiment = max(vs, key=vs.get)

        row['sentiment'] = sentiment
        row['score'] = score
    return data

def finbert_sentiment(data):
    happy_tc = HappyTextClassification("BERT", "ProsusAI/finbert", num_labels=3)  # Load model
    if len(data) == 0:
        return data
    for row in data:
        result = happy_tc.classify_text(row["content"][:512])
        sentiment = result.label
        score = result.score

        row['sentiment'] = sentiment
        row['score'] = score
    return data

def getDataSentiment(data, senti_type):
    if (senti_type == "flair"):
        data = flair_sentiment(data)
    elif (senti_type == "vader"):
        data = vader_sentiment(data)
    else:
        data = finbert_sentiment(data)
    return data

# Helper
def getResponse(data, senti_type):
    cleanedData = getCleanedContent(data)
    sentimentData = getDataSentiment(cleanedData, senti_type)
    score = sentiment_score(sentimentData, senti_type)
    return jsonify({"data": sentimentData, "score": score})

# Average Sentiment 24 hours
def sentiment_score(dct, senti_type):
    if len(dct) == 0:
        return 0
    sentiment = []
    score = []

    for post in dct:

        if senti_type == "vader":
            score.append(float(post['score']))
        else:
            sentiment.append(post['sentiment'])
            score.append(float(post['score']))

    if (senti_type == "vader"):
        return statistics.mean(score)
    else:
        df = pd.DataFrame({'sentiment':sentiment, 'score':score})

        for index, row in df.iterrows():
            if row['sentiment'].lower() == 'negative':
                df.at[index,"score"] = 0 - row['score']
            else:
                df.at[index,"score"] = row['score']

        return df['score'].mean()


def autoArimaML(symbol, df):

    close = df['Close']
    # splitting the data
    train_ratio = 0.8
    train_size = int(df.shape[0] * train_ratio)
    test_size = df.shape[0] - train_size

    train = close.head(train_size)
    test = close.tail(test_size)

    model = auto_arima(train, start_p=1, start_q=1,max_p=6, max_q=3, m=12, seasonal=True, error_action='ignore',suppress_warnings=True)
    model.fit(train)

    forecast = model.predict(n_periods=test_size)

    todayPredict = forecast[-1]
    ytdClose = test[symbol][-1]
    MSE_error = mean_squared_error(test, forecast)

    return todayPredict, ytdClose, MSE_error

def arima(symbol, df):

    # preprocessing data
    train_data, test_data = df[0:int(len(df)*0.8)], df[int(len(df)*0.8):]
    training_data = train_data['Close'].values
    test_data = test_data['Close'].values
    history = [x for x in training_data]
    model_predictions = []
    N_test_observations = len(test_data)
    yhat = 0
    # train model
    for time_point in range(N_test_observations):
        try:
            model = ARIMA(history, order=(4,1,0))
            model_fit = model.fit()
            output = model_fit.predict()
            print(output)
            yhat = output[0]
            true_test_value = test_data[time_point]
            history.append(true_test_value)
            model_predictions.append(yhat)
        except Exception as e: 
            print(e)
            today_prediction = yhat
    
    model_predictions = pd.DataFrame(model_predictions,columns=['Prediction'])
    print(model_predictions)
    test = pd.DataFrame(test_data, columns = [symbol])

    # calculating rmse
    MSE_error = mean_squared_error(test, model_predictions)

    return model_predictions[0], test_data[-1], MSE_error
    


def prophet(symbol, df):
    return "hello"


def LSTM(symbol, df):
    return "hello"


def predict_price(symbol, ml_model):
    
    start_date = '2019-01-01'

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    end_date = yesterday

    panel_data = data.DataReader([symbol], 'yahoo', start_date, end_date)
    
    # ml model: auto arima, arima, prohphet, linear regression, LSTM
    if ml_model == 'autoarima':
        return autoArimaML(symbol, panel_data)
    elif ml_model == 'arima':
        return arima(symbol, panel_data)
    elif ml_model == 'prophet':
        return prophet(symbol, panel_data)
    elif ml_model == 'LSTM':
        return LSTM(symbol, panel_data)

@app.route("/api/<string:source>/<string:symbol>/<string:senti_type>/<string:ml_type>/")
def mainFunction(source, symbol, senti_type, ml_type):
    todayPredict, ytdClose, MSE_error = predict_price(symbol, ml_type)
    print(todayPredict)
    # predict_price(symbol, ml_type)
    return "hello"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
