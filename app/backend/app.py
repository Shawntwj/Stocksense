# remember to pip install:
    # flask
    # git+https://github.com/JustAnotherArchivist/snscrape.git
    # GoogleNews
    # newspaper3k
    # flair
    # happytransformer

import time
import datetime as datetime
from datetime import datetime as dt
from flask import Flask
from flask import jsonify
import pandas as pd

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


app = Flask(__name__)


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

@app.route('/scraper/stocktwits/<string:symbol>/<string:start_date>/<string:end_date>/')
def getStocktwits(symbol, start_date, end_date):
    if (first_check(symbol)):
        data = []
        start_date = dt.strptime(start_date, "%Y-%m-%d")
        end_date = dt.strptime(end_date, "%Y-%m-%d")
        j = 0   # page number

        while end_date >= start_date:
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

                    start_date = dt.strptime(date_created_data, "%Y-%m-%d")

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
        cleanedData = getCleanedContent(data)
        sentimentData = getDataSentiment(cleanedData)
        return jsonify({"data": sentimentData})

# News scraper - NOT TESTED YET!!!!
def getArticleSummary(parsed_news):
    data=[]
    for ind in parsed_news:
        dicti={}
        article = Article(ind[1],config=config)
        try:
            article.download()
            article.parse()
            article.nlp()

            dicti['ticker']=ind[0]
            dicti['title']=article.title
            dicti['content']=article.text
            dicti['summary']=article.summary
            dicti['link']=ind[1]
            if article.publish_date == None:
                dicti['date']=date
            else:
                dicti['date']=article.publish_date
                date = article.publish_date
            data.append(dicti)
        except:
            pass

    return data

def getGoogleNewsLinks(symbol, start_date, end_date):
    parsed_news = []

    start_date = dt.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y')
    end_date = dt.strptime(end_date, '%Y-%m-%d').strftime('%m/%d/%Y')

    googlenews=GoogleNews(start = start_date, end = end_date) #month/day/year
    googlenews.search(symbol)

    for i in range(2, 20):
        googlenews.getpage(i)
        result=googlenews.result()
        df=pd.DataFrame(result)

    for ind in df.index:
        link = df['link'][ind]
        parsed_news.append([symbol, link])

    return parsed_news

@app.route('/scraper/news/<string:symbol>/<string:start_date>/<string:end_date>/')
def getNews(symbol, start_date, end_date):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    config = Config()
    config.browser_user_agent = user_agent

    parsed_news = getGoogleNewsLinks(symbol, start_date, end_date)
    data = getArticleSummary(parsed_news)

    cleanedData = getCleanedContent(data)
    sentimentData = getDataSentiment(cleanedData)
    return jsonify({"data": sentimentData})

# Twitter scraper
@app.route('/scraper/twitter/<string:symbol>/<string:start_date>/<string:end_date>/')
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
    cleanedData = getCleanedContent(data)
    sentimentData = getDataSentiment(cleanedData)
    return jsonify({"data": sentimentData})

# Reddit scraper
def reddit_sentiment_comment(search, start, end, subreddit):
    api = PushshiftAPI()

    s = dt.strptime(start, '%d/%m/%Y')
    e = dt.strptime(end, '%d/%m/%Y')
    start_date = time.mktime(dt.strptime(start, "%d/%m/%Y").timetuple())
    end_date = time.mktime(dt.strptime(end, "%d/%m/%Y").timetuple())
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
                    'created':dt.fromtimestamp(comment.created)
                })  # Retrieve post data and append to dataframe
        except:
            continue # Continue loop if error is found

    return comments

def reddit_sentiment_post(search, start, end, subreddit):
    api = PushshiftAPI()
    s = dt.strptime(start, '%d/%m/%Y')
    e = dt.strptime(end, '%d/%m/%Y')
    start_date = time.mktime(dt.strptime(start, "%d/%m/%Y").timetuple())
    end_date = time.mktime(dt.strptime(end, "%d/%m/%Y").timetuple())
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
                    'created':dt.fromtimestamp(post.created)
                })  # Retrieve post data and append to dataframe
        except:
            continue # Continue loop if error is found

    return posts

def getReddit(redditType, symbol, start_date, end_date):
    """convert date format to %d/%m/%Y"""
    start = "/".join(start_date.split("-")[::-1])
    end = "/".join(end_date.split("-")[::-1])
    sub = "stocks"
    if redditType == "comment":
        data = reddit_sentiment_comment(symbol, start, end, sub)
    elif  redditType == "post":
        data = reddit_sentiment_post(symbol, start, end, sub)
    cleanedData = getCleanedContent(data)
    return jsonify({"data": cleanedData, "sentiment": getDataSentiment(cleanedData)})

@app.route('/scraper/reddit/comment/<string:symbol>/<string:start_date>/<string:end_date>/')
def getRedditComments(symbol, start_date, end_date):
    return getReddit("comment", symbol, start_date, end_date)

@app.route('/scraper/reddit/post/<string:symbol>/<string:start_date>/<string:end_date>/')
def getRedditPosts(symbol, start_date, end_date):
    return getReddit("post", symbol, start_date, end_date)

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
def flair_senitment(data):
    flair_sentiment = flair.models.TextClassifier.load('en-sentiment')  # Load model
    for row in data:
        s = flair.data.Sentence(row["content"])
        flair_sentiment.predict(s)
        sentiment = str(s.labels[0]).split()[0]
        score = str(s.labels[0]).split()[1][1:-1]

        row["flair_sentiment"] = sentiment
        row["flair_sentiment_score"] = score

    return data

def vader_senitment(data):
    sia = SentimentIntensityAnalyzer()  # Load model
    for row in data:
        vs = sia.polarity_scores(row["content"])
        score = vs["compound"]
        del vs['compound']
        sentiment = max(vs, key=vs.get)

        row['vader_sentiment'] = sentiment
        row['vader_score'] = score
    return data

def finbert_senitment(data):
    happy_tc = HappyTextClassification("BERT", "ProsusAI/finbert", num_labels=3)  # Load model
    for row in data:
        result = happy_tc.classify_text(row["content"])
        sentiment = result.label
        score = result.score

        row['finbert_sentiment'] = sentiment
        row['finbert_score'] = score
    return data

def getDataSentiment(data):
    data = flair_senitment(data)
    data = vader_senitment(data)
    data = finbert_senitment(data)
    return data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
