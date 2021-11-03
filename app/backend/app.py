#remember to pip install:
# flask
# git+https://github.com/JustAnotherArchivist/snscrape.git
# GoogleNews
# newspaper3k

from flask import Flask
from flask import jsonify
import pandas as pd
import ast
import time

# libraries for Stocktwits
import requests
import json
import os
import datetime as datetime
from datetime import datetime as dt

# libraries for News
from GoogleNews import GoogleNews
from newspaper import Article
from newspaper import Config

# libraries for Twitter
import snscrape.modules.twitter as sntwitter

# libraries for Reddit


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

        j = 0

        while end_date > start_date:
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

            print(j,"page done")
            j += 1

        return jsonify({"data": data})

# News scraper
def getArticleSummary(parsed_news):

    data=[]
    for ind in parsed_news:
        dicti={}
        article = Article(ind[1],config=config)
        try:
            article.download()
            article.parse()
            article.nlp()

            dicti['Ticker']=ind[0]
            dicti['Title']=article.title
            dicti['Article']=article.text
            dicti['Summary']=article.summary
            dicti['Link']=ind[1]
            if article.publish_date == None:
                dicti['Date'] = date
            else:
                dicti['Date']= article.publish_date
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
        print(result)
    
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

    return jsonify({"data": data})

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
