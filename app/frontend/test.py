import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data
from sklearn.metrics import mean_squared_error
from fastai.tabular.all import *
import datetime
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