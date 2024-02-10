from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from flask_caching import Cache
from feedgen.feed import FeedGenerator
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


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('index'))
    data = {
        'query': query
    }
    return render_template('search.html', data=data)


@app.route('/rss')
def rss():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('index'))
    data = fetch_data(query)
    fg = FeedGenerator()
    fg.id('https://news-analyzer.com/rss')
    fg.title('News Analyzer')
    fg.author({'name': 'Oleksii Nakhod', 'email': 'alexey.nakhod@gmail.com'})
    fg.subtitle('News analysis using NLP')
    fg.link(href=url_for('rss', q=query), rel='self')
    fg.link(href=url_for('search', q=query), rel='alternate')
    fg.description('News analysis using NLP')
    fg.language('en')

    for article in data['articles']:
        fe = fg.add_entry()
        fe.id(article['url'])
        fe.link(href=article['url'])
        fe.title(article['title'])
        fe.description(article['description'])
        fe.pubDate(article['publishedAt'])

    rss_feed = fg.rss_str(pretty=True)
    response = Response(rss_feed, content_type='application/rss+xml')
    return response


@app.route('/get-matches', methods=['GET'])
def get_matches():
    query = request.args.get('q')
    return fetch_data(query)
    

def fetch_data(query):
    url = 'https://newsapi.org/v2/everything'
    cache_key = f'newsapi_get_matches_{query}'
    cached_data = cache.get(cache_key)
    if cached_data:
        app.logger.info('Cache hit! Returning cached data.')
        return cached_data
    
    app.logger.info('Cache miss! Fetching data from News API.')
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
        app.logger.error('Please provide a valid News API key in the NEWSAPI_KEY environment variable.')
        return jsonify({
            'error': 'Please provide a valid News API key in the NEWSAPI_KEY environment variable.'
        }), 401
    
    else:
        return jsonify(response.json()), response.status_code
    

@app.errorhandler(404)
def handle_404(e):
    return redirect(url_for('index'))


@app.errorhandler(500)
def handle_500(e):
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)