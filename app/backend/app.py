#remember to pip install:
# flask
# git+https://github.com/JustAnotherArchivist/snscrape.git

from flask import Flask
from flask import jsonify
import pandas as pd
import ast

# libraries for Stocktwits
import requests
import json
import time
import os
import datetime as datetime
from datetime import datetime as dt

# libraries for News

# libraries for Twitter
import snscrape.modules.twitter as sntwitter

# libraries for Reddit

# packages: flair
import flair
from flair.models import TextClassifier
from flair.data import Sentence

# packages: vader
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# packages: finbert
# from finbert_embedding.embedding import FinbertEmbedding
from happytransformer import HappyTextClassification 


app = Flask(__name__)


def vader(jsonthing):
    sid_obj = SentimentIntensityAnalyzer()
    for json in jsonthing["data"]:
        result = sid_obj.polarity_scores(json["content"])
        score = result["compound"]
        if vader_compund_score > 0:
            sentiment = "Positive"
        elif vader_compund_score < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        json["vader_score"] = score
        json["vader_sentiment"] = sentiment
    return jsonthing

def finbert(jsonthing):
    happy_tc = HappyTextClassification("BERT", "ProsusAI/finbert", num_labels=3)
    for json in jsonthing["data"]:  
        result = happy_tc.classify_text(json["content"])
        sentiment = result.label
        score = result.score
        json['finbert_sentiment'] = sentiment
        json['finbert_score'] = score
    return jsonthing

def flair(jsonthing):

    flair_sentiment = TextClassifier.load('en-sentiment')
    for json in jsonthing["data"]: 
        s = Sentence(json["content"])
        flair_sentiment.predict(s) 
        sentiment = str(s.labels[0]).split()[0]
        score = str(s.labels[0]).split()[1][1:-1]
        json['flair_sentiment'] = sentiment
        json['flair_score'] = score
    return jsonthing
    
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

@app.route('/scraper/stocktwits/<string:symbol>/')
def getStocktwits(symbol):
    if (first_check(symbol)):

        scraped_data = { "data": [] }

        post_date = dt.now()
        previous = post_date - datetime.timedelta(days=1)

        j = 0

        while post_date > previous:
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
                    print(date_created_data)

                    post_date = dt.strptime(date_created_data, "%Y-%m-%d")

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

                    scraped_data["data"].append({
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

            print(j,"page done")
            j += 1

        # test = vader(scraped_data)
        test = flair(scraped_data)
        return  test

# News scraper
@app.route('/scraper/news/<string:symbol>/')
def getNews(symbol):
    pass

# Twitter scraper
@app.route('/scraper/twitter/<string:symbol>/<string:start_date>/<string:end_date>')
def getTwitter(symbol, start_date, end_date):
    """
    Using TwitterSearchScraper to scrape data and append tweets to list
    - assumes date format to be YYYY-MM-DD
    - end date exclusive for twitter
    - with conditions: min word length = 5, min like = 200, min followers = 50, min retweet = 5
    """
    data = []
    items = sntwitter.TwitterSearchScraper(f"{symbol} since:{start_date} until:{end_date}").get_items()
    for i,tweet in enumerate(items):
        print(tweet.content)
        if len(tweet.content.split())>=5 and tweet.likeCount>=200 and tweet.user.followersCount>=50 and tweet.retweetCount>=5:
            data.append({
                "username": tweet.user.username,
                "content": tweet.content,
                "datetime": tweet.date,
                'followers': tweet.user.followersCount,
                'comments': tweet.replyCount,
                'shares': tweet.retweetCount,
                'likes': tweet.likeCount
            })
    return jsonify({"data": data})

# Reddit scraper
@app.route('/scraper/reddit/<string:symbol>/')
def getReddit(symbol):
    pass

# put trained models on flask 
# sentiment analysis 

# two options - dont train just put the model inside here 
#  - train and put the model here and run the data through it 



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
