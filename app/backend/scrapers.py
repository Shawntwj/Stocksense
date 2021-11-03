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


@app.route('/stocktwits/<string:symbol>/')
    # methods go here
    def getStocktwits(symbol)
    pass

@app.route('/news/<string:symbol>/')
    # methods go here
    def getNews(symbol)
    pass

@app.route('/twitter/<string:symbol>/')
    # methods go here
    def getTwitter(symbol)
    pass

@app.route('/reddit/<string:symbol>/')
    # methods go here
    def getReddit(symbol)
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # run our Flask app