# import library
import requests
import pandas as pd
import json
import csv
import time
import os
import requests
import datetime as datetime
from datetime import datetime as dt

def first_check(symbol):
    url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json?filter=top&limit=20"
    req = requests.get(url)
    data_dict = req.json()
    if data_dict["response"]["status"] == 200:
        return True
    return False

symbol = "amzn"
scrape_till = datetime.datetime(2021, 10, 10)

def scrapeStockTwits(symbol, scrape_till):
    if (first_check):
        csvFile = open(f"{symbol}_posts.csv", "w", newline='', encoding="utf-8-sig")
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(("person_id","content","date_created","time_created","username","name","join_date","official","followers","upload_source","likes"))

        post_date = dt.now()
        j = 0

        while post_date > scrape_till:
            url = "https://api.stocktwits.com/api/2/streams/symbol/AMZN.json?filter=top&limit=40"
            if j > 0:
                url += postid

            req = requests.get(url)
            data_dict = req.json()

            if data_dict["response"]["status"] == 200:
                main_body = data_dict["messages"]
                for i in range(len(main_body)):
                    person_id = main_body[i]["id"]
                    content = main_body[i]["body"]

                    content = content.replace("’", "'")
                    content = content.replace("&#39;","'")

                    time = main_body[i]["created_at"]
                    timelist = time.split("T")

                    date_created = timelist[0]
                    print(date_created)

                    post_date = dt.strptime(date_created, "%Y-%m-%d")

                    time_created = timelist[1][:-1]

                    username = main_body[i]["user"]["username"]
                    name = main_body[i]["user"]["name"]
                    join_date = main_body[i]["user"]["join_date"]
                    official = main_body[i]["user"]["official"]
                    followers = main_body[i]["user"]["followers"]
                    source =  main_body[i]["source"]["title"]
                    try:
                        likes =  main_body[i]["likes"]["total"]
                    except:
                        likes = 0

                    postid = data_dict["cursor"]["max"]
                    postid = "&max=" + str(postid)

                    csvWriter.writerow((person_id,content,date_created,time_created,username,name,join_date,official,followers,source,likes))

            print(j,"page done")
            j += 1

scrapeStockTwits(symbol, scrape_till)