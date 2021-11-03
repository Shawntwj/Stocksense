from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
app = Flask(__name__)
api = Api(app)

class Stocktwits(Resource):
    # methods go here
    pass
    
class News(Resource):
    # methods go here
    pass

class Twitter(Resource):
# methods go here
pass
    
class Reddit(Resource):
    # methods go here
    pass
    
api.add_resource(Stocktwits, '/stocktwits')  # entry point for Stocktwits
api.add_resource(News, '/news')  # entry point for News
api.add_resource(Twitter, '/twitter')  # entry point for Stocktwits
api.add_resource(Reddit, '/reddit')  # entry point for News


if __name__ == '__main__':
    app.run()  # run our Flask app