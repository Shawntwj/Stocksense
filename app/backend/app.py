"""
if running the app for the first time: run
`pip install -r requirements.txt`
in this folder to install the packages needed
"""

import time
import datetime
from flask import Flask
from flask import jsonify
from flask_cors import CORS
import pandas as pd
import statistics
from collections import Counter

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
from fbprophet import Prophet
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM


app = Flask(__name__)
CORS(app)



@app.route("/api/<string:source>/<string:symbol>/<string:senti_type>/<string:ml_type>/")
def mainFunction(source, symbol, senti_type, ml_type):
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
    data = response["data"]
    sentiment = response["score"]
    senti_grouped = response["senti_grouped"]

    # extract correlation score from exported excel
    if source == 'twitter' and symbol == 'msft':
        correlation = 0
    else:
        if senti_type == 'flair':
            senti_key = 'Flair Sentiment'
        else:
            senti_key = senti_type.capitalize()
        corr_df = pd.read_excel("sentiment_correlation.xlsx")
        platform_corr_df = corr_df[corr_df['Platform']==source]
        row_corr_df = platform_corr_df[platform_corr_df['Ticket']==symbol.upper()]
        corr_series = row_corr_df[senti_key+' Score']
        correlation = corr_series.values[0]

    # ML models
    todayPredict, ytdClose, MSE_error = predict_price(symbol, ml_type)

    decision = decision_tree(sentiment, correlation, todayPredict, ytdClose)

    # wordcloud
    words_li = []
    for obj in data:
        words_li += obj["content"].split()
    dic = Counter(words_li)
    # most_occur = dic.most_common(5)
    words = []
    for [k,v] in dic.items():
        words.append({"text":k, "value":v})

    return jsonify({"decision":decision, "error":MSE_error, "todayPredict":todayPredict, "ytdClose":ytdClose, "score": sentiment, "words":words, "data":senti_grouped, "corr": correlation})

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

# @app.route('/api/stocktwits/<string:symbol>/<string:senti_type>/')
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
                    # person_id_data = main_body[i]["id"]
                    content_data = main_body[i]["body"]

                    content_data = content_data.replace("’", "'")
                    content_data = content_data.replace("&#39;","'")

                    newdatetime = main_body[i]["created_at"]
                    formatfrom="%Y-%m-%dT%H:%M:%SZ"
                    formatto="%a %d %b %Y, %H:%M:%S GMT"
                    newdatetime = datetime.datetime.strptime(newdatetime,formatfrom).strftime(formatto)

                    time = main_body[i]["created_at"]
                    timelist = time.split("T")

                    date_created_data = timelist[0]

                    start_date = datetime.datetime.strptime(date_created_data, "%Y-%m-%d")

                    # if (start_date == end_date):

                    # time_created_data = timelist[1][:-1]

                    # username_data = main_body[i]["user"]["username"]
                    # name_data = main_body[i]["user"]["name"]
                    # join_date_data = main_body[i]["user"]["join_date"]
                    # official_data = main_body[i]["user"]["official"]
                    # followers_data = main_body[i]["user"]["followers"]
                    # source_data =  main_body[i]["source"]["title"]
                    # try:
                    #     likes_data =  main_body[i]["likes"]["total"]
                    # except:
                    #     likes_data = 0

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

        return getResult(data, senti_type)

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

            # dicti['title']=article.title
            dicti['content']=article.text
            # dicti['summary']=article.summary
            # dicti['link']=ind[1]
            if article.publish_date == None:
                dicti['datetime']=start_date
            else:
                dicti['datetime']=article.publish_date

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

# @app.route('/api/news/<string:symbol>/<string:senti_type>/')
def getNews(symbol, senti_type):
    start_date = datetime.datetime.now()
    parsed_news = getGoogleNewsLinks(symbol, start_date)
    data = getArticleSummary(parsed_news, start_date)
    return getResult(data, senti_type)

# Twitter scraper
# @app.route('/api/twitter/<string:symbol>/<string:senti_type>/')
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
                # "username": tweet.user.username,
                "content": tweet.content,
                "datetime": tweet.date,
                # "followers": tweet.user.followersCount,
                # "comments": tweet.replyCount,
                # "shares": tweet.retweetCount,
                # "likes": tweet.likeCount
            })

    return getResult(data, senti_type)

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
                    # 'username':comment.author_fullname,
                    # 'score':comment.score,
                    # 'comment_id':comment.id,
                    # 'subreddit':comment.subreddit,
                    # 'parent_id':comment.parent_id,
                    'datetime':datetime.datetime.fromtimestamp(comment.created)
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
                    # 'title':post.title,
                    # 'score':post.score,
                    # 'upvote_ratio':post.upvote_ratio,
                    # 'id':post.id,
                    # 'subreddit':post.subreddit,
                    # 'url':post.url,
                    # 'num_comments':post.num_comments,
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
    return getResult(data, senti_type)

# @app.route('/api/reddit:comment/<string:symbol>/<string:senti_type>/')
def getRedditComments(symbol, senti_type):
    return getReddit("comment", symbol, senti_type)

# @app.route('/api/reddit:post/<string:symbol>/<string:senti_type>/')
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
        if len(s.labels) == 0 | len(str(s.labels[0])) == 0:
            sentiment = 0
            score = 0
        else:
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

def getResult(data, senti_type):
    cleanedData = getCleanedContent(data)
    sentimentData = getDataSentiment(cleanedData, senti_type)
    score = sentiment_score(sentimentData, senti_type)
    senti_grouped = sentiment_by_datetime(sentimentData)
    return {"data": sentimentData, "score": score, "senti_grouped": senti_grouped}

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

# Average Sentiment by datetime
def sentiment_by_datetime(data):
	df = pd.DataFrame(data)
	df.datetime = pd.to_datetime(df.datetime)
	df['score'] = df['score'].astype(float)
	df2 = df.set_index('datetime').groupby([pd.Grouper(freq='H'), 'sentiment']).mean()
	df_dict = df2.to_dict()
	sentiment_group = {}

	for k, v in df_dict["score"].items():
		date2 = pd.to_datetime(k[0])
		inner = {}
		if date2 in sentiment_group:
			inner = sentiment_group[date2]
			inner[k[1]] = v
			sentiment_group[date2] = inner
		else:
			inner[k[1]] = v
			sentiment_group[date2] = inner

	new_group = []
	for key, val in sentiment_group.items():
		positive = 0
		negative = 0
		if 'POSITIVE' in val.keys():
			positive = val["POSITIVE"]
		if 'NEGATIVE' in val.keys():
			negative = val["NEGATIVE"]
		new_group.append({
			"date": key,
			"negative": negative,
			"positive": positive
		})

	return new_group

# ML models
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
            yhat = output[-1]
            true_test_value = test_data[time_point]
            history.append(true_test_value)
            model_predictions.append(yhat)
        except Exception as e:
            print(e)
            return 0, test_data[-1], 0

    model_pred = pd.DataFrame(model_predictions,columns=['Prediction'])
    test = pd.DataFrame(test_data, columns = [symbol])

    # calculating rmse
    MSE_error = mean_squared_error(test, model_pred)

    return model_predictions[-1], test_data[-1], MSE_error

def prophet(symbol, df):
    close = df['Close']

    #preparing data
    close.reset_index(inplace = True)
    close = close[['Date', symbol]]
    close.rename(columns={symbol: 'y', 'Date':'ds'}, inplace = True)

    #splitting the data
    train_ratio = 0.8
    train_size = int(df.shape[0] * train_ratio)
    test_size = df.shape[0] - train_size

    train = close.head(train_size)
    test = close.tail(test_size)

    #fit the model
    model = Prophet(daily_seasonality=True)
    model.fit(train)

    #predictions
    close_prices = model.make_future_dataframe(periods=len(test)+1)
    forecast = model.predict(close_prices)
    today_prediction = forecast['yhat'].to_list()[-1]

    # combine test and forecast dataframes
    forecast = pd.DataFrame(forecast,index = test.index,columns=['yhat'])
    result = pd.concat([forecast, test], axis = 1)

    #rmse
    forecast_valid = forecast['yhat'][-test_size:]
    MSE_error = mean_squared_error(test['y'], forecast_valid)

    # renaming columns in result
    result.rename(columns = {'yhat':'Prediction', 'y': symbol}, inplace = True)
    result.drop(columns = ['ds'], inplace = True)

    return today_prediction, test['y'].to_list()[-1], MSE_error

def lstm(symbol, df):
    close = df['Close']

    #preparing data
    close.reset_index(inplace = True)
    close = close[['Date', symbol]]

    #splitting the data
    train_ratio = 0.8
    train_size = int(df.shape[0] * train_ratio)
    test_size = df.shape[0] - train_size

    train = close.head(train_size)
    test = close.tail(-test_size)

    close.drop('Date', axis=1, inplace = True)

    #convert into x and y
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(close)

    x_train, y_train = [], []
    for i in range(60,len(train)):
        x_train.append(scaled_data[i-60:i,0])
        y_train.append(scaled_data[i,0])
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1)))
    model.add(LSTM(units=50))
    model.add(Dense(1))

    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=2)

    #prediction
    inputs = close[len(close) - len(test) - 60:].values
    inputs = inputs.reshape(-1,1)
    inputs  = scaler.transform(inputs)

    X_test = []
    for i in range(60,inputs.shape[0]+1):
        X_test.append(inputs[i-60:i,0])
    X_test = np.array(X_test)

    X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
    closing_price = model.predict(X_test)
    closing_price = scaler.inverse_transform(closing_price)
    today_prediction = closing_price[-1]
    closing_price = closing_price[:-1]

    #rmse
    MSE_error = mean_squared_error(test[symbol], closing_price)

    return today_prediction[0], closing_price[-1][0], MSE_error

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
        return lstm(symbol, panel_data)

def decision_tree(sentiment, correlation, predicted_price, yesterday_price):
    """
    sentiment score for 24hrs
    correlation score
    predicted price for the day
    yesterday's price
    """
    gate = 0
    if predicted_price > yesterday_price:
        gate += 1
    else:
        gate -= 1
    if sentiment >= 0:
        if correlation >= 0.2:
            gate += 1
        if correlation >= 0.4:
            gate += 2
        if correlation <= -0.2:
            gate -= 1
        if correlation <= -0.4:
            gate -= 2
    else:
        if correlation <= -0.2:
            gate += 1
        if correlation <= -0.4:
            gate += 2
        if correlation >= 0.2:
            gate -= 1
        if correlation >= 0.4:
            gate -= 2
    if gate >= 2:
        return "Buy"
    elif gate <= -2:
        return "Sell"
    else:
        return "Hold"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
