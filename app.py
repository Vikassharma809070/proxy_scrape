from flask import Flask, render_template, jsonify
from scrape_twitter import get_trending_topics, save_to_mongodb
import pymongo
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    try:
        trending_topics, ip_address = get_trending_topics()
        data = save_to_mongodb(trending_topics, ip_address)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/results')
def results():
    try:
        client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
        db = client['twitter_trends']
        collection = db['trends']
        latest_data = collection.find().sort('_id', -1).limit(1)[0]
        return render_template('results.html', data=latest_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
