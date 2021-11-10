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
# from keras.models import Sequential
# from keras.layers import Dense, Dropout, LSTM

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
    fivedaypredicted = test[symbol][-5:]
    MSE_error = mean_squared_error(test, forecast)

    graphData = [] 
    for index, row in fivedaypredicted.iteritems():
        dateobj = {"date":str(index.date()), "predicted":row }
        graphData.append(dateobj)
    return graphData
    return todayPredict, ytdClose, MSE_error

start_date = '2019-01-01'

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
end_date = yesterday

panel_data = data.DataReader(["AAPL"], 'yahoo', start_date, end_date)
test = autoArimaML("AAPL", panel_data)
print(test)
