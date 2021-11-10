# import datetime
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from pandas_datareader import data
# from sklearn.metrics import mean_squared_error
# from fastai.tabular.all import *
# import datetime
# from sklearn.linear_model import LinearRegression

import time
import datetime 
from flask import Flask
from flask import jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
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
# import re
# import nltk
# from nltk import word_tokenize
# from nltk.tokenize import RegexpTokenizer
# from nltk.stem import WordNetLemmatizer
# from nltk.corpus import stopwords
# nltk.download('stopwords')

# libraries for sentiment analysis
import flair
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from happytransformer import HappyTextClassification

# libraries for prediction
from pandas_datareader import data
from sklearn.metrics import mean_squared_error
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
# from fbprophet import Prophet
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
from fastai.tabular.all import add_datepart
from sklearn.linear_model import LinearRegression

def linear_regression(symbol, df):
    global data
#     tickers = [symbol]

#     start_date = '2019-01-01'
#     end_date = datetime.date.today() 

#     # User pandas_reader.data.DataReader to load data
#     panel_data = data.DataReader(tickers,'yahoo', start_date, end_date)

#     # df = panel_data['Close']
#     df = panel_data
    
    graph = df 

    df["Date"] = df.index
    df["Date"] = pd.to_datetime(df['Date'])

    df['Date'] = pd.to_datetime(df.Date,format='%Y-%m-%d')
    df.index = df['Date']

    #sorting
    data = df.sort_index(ascending=True, axis=0)

    #creating a separate dataset
    new_data = pd.DataFrame(index=range(0,len(df)),columns=['Date', 'Close'])

    

    for i in range(0,len(data)):
        new_data['Date'][i] = data['Date'][i]
        new_data['Close'][i] = data['Close'].iloc[i][symbol]

    graph = new_data[["Date","Close"]]
    #create features
    add_datepart(new_data, 'Date')
    new_data.drop('Elapsed', axis=1, inplace=True)  #elapsed will be the time stamp


    new_data['mon_fri'] = 0
    new_data
    for i in range(0,len(new_data)):
        if (new_data['Dayofweek'][i] == 0 or new_data['Dayofweek'][i] == 4):
            new_data.at[i,'mon_fri'] = 1
        else:
            new_data.at[i,'mon_fri'] = 0


    end = int(len(new_data) * 0.8)

    train = new_data[:end]
    valid = new_data[end:]

    x_train = train.drop('Close', axis=1)
    y_train = train['Close']
    x_valid = valid.drop('Close', axis=1)
    y_valid = valid['Close']

    model = LinearRegression()
    model.fit(x_train,y_train)


    #make predictions and find the rmse
    preds = model.predict(x_valid)
    rms=np.sqrt(np.mean(np.power((np.array(y_valid)-np.array(preds)),2)))


    yst_price = panel_data.iloc[-2]["Close"][symbol]

    tdy = pd.DataFrame([datetime.date.today()],columns=["Date"])

    add_datepart(tdy, 'Date')
    tdy.drop('Elapsed', axis=1, inplace=True)  #elapsed will be the time stamp
    tdy['mon_fri'] = 1
    if (tdy['Dayofweek'][0] == 0 or tdy['Dayofweek'][0] == 4):
        tdy['mon_fri'] = 1
    else:
        tdy['mon_fri'] = 0

    
    train = graph[:end]
    test = graph[end:]
    graphData = []
    for index, row in train.iterrows():
        dateobj = {"date":str(row[0].date()), "train":row[1] }
        graphData.append(dateobj)
        

    i = 0
    for index, row in test.iterrows():

        dateobj = {"date":str(row[0].date()), "test":row[1], "predicted":preds[i] }
        graphData.append(dateobj)
        i += 1


    tdy_preds = model.predict(tdy)
    tdy_preds
    json_result = {'today_price': tdy_preds, 'yesterday_price':yst_price, 'rmse': rms, }

    return tdy_preds, yst_price, rms, graphData

start_date = '2019-01-01'

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
end_date = yesterday

panel_data = data.DataReader(["AAPL"], 'yahoo', start_date, end_date)

test = linear_regression("AAPL",panel_data)
print(test)
# ---------------------------------------------------------
# def arima(symbol, df):
#     # preprocessing data
#     train_data, test_data = df[0:int(len(df)*0.8)], df[int(len(df)*0.8):]
#     graph_data = test_data['Close'] 
#     training_data = train_data['Close'].values
#     test_data = test_data['Close'].values
#     history = [x for x in training_data]
#     model_predictions = []
#     N_test_observations = len(test_data)
#     yhat = 0
#     # train model
#     for time_point in range(N_test_observations):
#         try:
#             model = ARIMA(history, order=(4,1,0))
#             model_fit = model.fit()
#             output = model_fit.predict()
#             yhat = output[-1]
#             true_test_value = test_data[time_point]
#             history.append(true_test_value)
#             model_predictions.append(yhat)
#         except Exception as e:
#             print(e)
#             return 0, test_data[-1], 0

#     model_pred = pd.DataFrame(model_predictions,columns=['Prediction'])
#     test = pd.DataFrame(test_data, columns = [symbol])

#     # calculating rmse
#     MSE_error = mean_squared_error(test, model_pred)

#     graphData = []
#     for index, row in train_data['Close'].iterrows():
#         dateobj = {"date":str(index.date()), "train":row[0] }
#         graphData.append(dateobj)

#     i = 0
#     for index, row in graph_data.iterrows():
#         dateobj = {"date":str(index.date()), "test":row[0], "predicted":model_predictions[i] }
#         graphData.append(dateobj)
#         i += 1


#     return model_predictions[-1], test_data[-1], MSE_error, graphData


# test = arima("AAPL",panel_data)
# print(test)

