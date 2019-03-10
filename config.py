from flask import Flask
from pymongo import MongoClient


client = MongoClient('localhost:27017')
db = client.PlanetDB

app = Flask(__name__)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')