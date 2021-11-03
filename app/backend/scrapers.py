from flask import Flask
from flask import jsonify
import pandas as pd
import ast

# libraries for stocktwits
import requests
import json
import time
import os
import datetime as datetime
from datetime import datetime as dt


app = Flask(__name__)


@app.route('/scraper/stocktwits/<string:symbol>/')
def getStocktwits(symbol):
    pass

@app.route('/scraper/news/<string:symbol>/')
def getNews(symbol):
    pass

@app.route('/scraper/twitter/<string:symbol>/')
def getTwitter(symbol):
    pass

@app.route('/scraper/reddit/<string:symbol>/')
def getReddit(symbol):
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
