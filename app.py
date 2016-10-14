#!/usr/bin/env python3

from flask import Flask, Blueprint, jsonify, request, abort
import json
from lib.utils import load_config, timestamp_today, timestamp_day_decrement, timestamp_to_date, normalize_word
from lib.logger import Logger
from lib.mongo_connector import MongoConnector
from crawler import Crawler
import math

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/')
def index():
    return jsonify({'handlers': ['update', 'users', 'posts', 'idf']})


@api.route('/update')
def update():
    try:
        crawler.update_database()
    except Exception as e:
        return jsonify({'message': 'update failed'}), 400
    return jsonify({'message': 'update successful'})


@api.route('/users')
def authors():
    start_timestamp = int(request.args.get('start') or timestamp_day_decrement())
    end_timestamp = int(request.args.get('end') or timestamp_today())
    return jsonify({'users': mongo.filter_users_by_time(start_timestamp, end_timestamp)})


@api.route('/posts')
def posts():
    start_timestamp = int(request.args.get('start') or timestamp_day_decrement())
    end_timestamp = int(request.args.get('end') or timestamp_today())
    user = request.args.get('user')
    if not user:
        return jsonify({'message': 'user name not specified'}), 400
    return jsonify({'user': user, 'posts': mongo.filter_posts_by_user(user, start_timestamp, end_timestamp)})


@api.route('/idf')
def idf():
    start_timestamp = int(request.args.get('start') or timestamp_day_decrement())
    end_timestamp = int(request.args.get('end') or timestamp_today())
    word = normalize_word(request.args.get('word').lower())
    if not word:
        return jsonify({'message': 'word not specified'}), 400
    index_by_documents = mongo.filter_index_by_documents(start_timestamp, end_timestamp)
    documents_number = len(index_by_documents)
    documents_with_word = 0
    for document_index in index_by_documents:
        if word in document_index:
            documents_with_word += 1
    if documents_with_word == 0:
        return jsonify({'message': 'word does not appear in documents'}), 400
    idf = math.log10(documents_number / documents_with_word)
    return jsonify({'word': word, 'idf': idf})


if __name__ == '__main__':
    mongo = MongoConnector(load_config('conf/db.conf.json'))
    logger = Logger('logs/debug.log').log

    config = load_config('conf/app.conf.json')
    assert isinstance(config['port'], int)

    crawler = Crawler(load_config('conf/crawler.conf.json'))

    app = Flask(__name__)
    app.register_blueprint(api)
    app.run(host=config['host'], port=config['port'], debug=True)
