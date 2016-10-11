#!/usr/bin/env python3

from flask import Flask, Blueprint, jsonify, request
import json
from pymongo import MongoClient
from lib.data_converter import str2date, date2timestamp
from lib.logger import Logger
from lib.mongo_connector import MongoConnector

api = Blueprint('api', __name__, url_prefix = '/api')

@api.route('/authors/', methods=['GET'])
def authors():
    authors = {data['author']: data['data'] for data in mongo_connector.articles.find()}
    return jsonify(authors)

if __name__ == '__main__':
    logger = Logger()
    mongo_connector = MongoConnector()
    app = Flask(__name__)
    app.register_blueprint(api)
    app.run(host='::', port=5000, debug=True)
