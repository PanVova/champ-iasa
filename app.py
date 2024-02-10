from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
import logging
import os
from dotenv import load_dotenv
import requests


app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app.logger.info('Logging setup complete')

cache = Cache(
    app,
    config={
        'CACHE_TYPE': 'FileSystemCache',
        'CACHE_DIR': 'cache',
        'CACHE_DEFAULT_TIMEOUT': 86400
    }
)

load_dotenv()
newsapi_key = os.environ.get('NEWSAPI_KEY')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/get-matches', methods=['GET'])
def get_matches():
    url = 'https://newsapi.org/v2/everything'
    query = request.args.get('q')
    cache_key = f'newsapi_get_matches_{query}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    response = requests.get(
        url,
        params={
            'q': query,
            'apiKey': newsapi_key
        }
    )
    
    if response.status_code == 200:
        cache.set(cache_key, response.json())
        return jsonify(response.json()), response.status_code
    
    elif response.status_code == 401 and response.json()['code'] == 'apiKeyInvalid':
        app.logger.error('Please provide a valid News API key in the environment variable NEWSAPI_KEY')
        return jsonify({
            'error': 'Please provide a valid News API key in the environment variable NEWSAPI_KEY'
        }), 401
    
    else:
        return jsonify(response.json()), response.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)