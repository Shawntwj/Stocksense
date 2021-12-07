import time
import datetime
from flask import Flask
from flask import jsonify
from flask_cors import CORS

# libraries for Stocktwits
import requests
import json
import os

# libraries for Twitter
import snscrape.modules.twitter as sntwitter
import twint
import nest_asyncio
import datetime as dt
import os
nest_asyncio.apply()

# @app.route("/api/<string:source>/<string:symbol>/<string:senti_type>/<string:ml_type>/")
def scrapper(source, symbol, senti_type, ml_type):
    """assumes values correspond to the excel & all lowercase"""
    # scrape, clean, sentiment analysis
    if source == 'news':
        response = getNews(symbol, senti_type)
    elif source == 'stocktwits':
        response = getStocktwits(symbol, senti_type)
    elif source == 'twitter':
        response = getTwitter(symbol, senti_type)
    elif source == 'reddit:comment':
        response = getRedditComments(symbol, senti_type)
        source = 'reddit'
    elif source == 'reddit:post':
        response = getRedditPosts(symbol, senti_type)
        source = 'reddit'

def getStocktwits(symbol, senti_type):
    data = []

    # start & end date will be set to only reflect the past 24 hours
    start_date = datetime.datetime.now()
    end_date = start_date - datetime.timedelta(days=1)

    j = 0   # page number
    postid = ''

    # the start date will be replaced by the last entry's created date
    # once it is more or equal to end date the loop will stop has to be done as URL only returns 40 posts at a time
    while start_date >= end_date:
        # URL to pull JSON data 
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json?filter=top&limit=40"

        # to ensure the original link  initialized above gets used
        if j > 0:
            # new URL after this will reflect https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json?filter=top&limit=40&max={max_post_ID}
            url += postid

        req = requests.get(url)
        data_dict = req.json()

        if data_dict["response"]["status"] == 200:
            main_body = data_dict["messages"]
            # looping through the main data 
            for i in range(len(main_body)):
                content_data = main_body[i]["body"]
                content_data = content_data.replace("’", "'")
                content_data = content_data.replace("&#s;","'")

                newdatetime = main_body[i]["created_at"]
                formatfrom="%Y-%m-%dT%H:%M:%SZ"
                formatto="%a %d %b %Y, %H:%M:%S GMT"
                newdatetime = datetime.datetime.strptime(newdatetime,formatfrom).strftime(formatto)

                time = main_body[i]["created_at"]
                timelist = time.split("T")

                date_created_data = timelist[0]

                start_date = datetime.datetime.strptime(date_created_data, "%Y-%m-%d")

                postid = data_dict["cursor"]["max"]
                postid = "&max=" + str(postid)

                data.append({
                    # "person_id": person_id_data,
                    "content": content_data,
                    "datetime": newdatetime,
                    # "date_created": date_created_data,
                    # "time_created": time_created_data,
                    # "username": username_data,
                    # "name": name_data,
                    # "join_date": join_date_data,
                    # "official": official_data,
                    # "followers": followers_data,
                    # "source": source_data,
                    # "likes": likes_data
                })
        j += 1

    return data


def getTwitter(symbol, senti_type):

    start_date = datetime.datetime.now()
    start_date = start_date - datetime.timedelta(days=1)
    
    t = twint.Config()
    t.Search = symbol
    # t.Geo = "1.290270,103.851959,15km"

    t.Since=start_date.strftime('%Y-%m-%d')
    # t.Until=end_date.strftime('%Y-%m-%d')
    
    t.Lang = "en"
    t.Filter_retweets = True 
    t.Custom["tweet"] = ["tweet", "username", "date", "time", "likes_count"]
    t.Store_object = True

    twint.run.Search(t)
    tweets = twint.output.tweets_list
    print(tweets)
    
    data = []
    for tweet in tweets:
        print(dir(tweet))
        data.append({
            "content": tweet.tweet,
            "datetime": tweet.datetime,
            "likes": tweet.likes_count,
            "username": tweet.username
        })
        
    return data
