from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from flask_caching import Cache
from feedgen.feed import FeedGenerator
import logging
import os
from dotenv import load_dotenv
import requests
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

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
    fg.id('https://content-analyzer.com/rss')
    fg.title('Content Analyzer')
    fg.author({'name': 'Oleksii Nakhod', 'email': 'alexey.nakhod@gmail.com'})
    fg.subtitle('Content analysis using NLP')
    fg.link(href=url_for('rss', q=query), rel='self')
    fg.link(href=url_for('search', q=query), rel='alternate')
    fg.description('Content analysis using NLP')
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
    content = get_content(query)
    return content


def check_cache(cache_key):
    cached_data = cache.get(cache_key)
    if cached_data:
        app.logger.info(f'{cache_key} cache hit! Returning cached data.')
        return cached_data
    else:
        app.logger.info(f'{cache_key} cache miss! Making a new request...')
        return None


def get_content(query):
    cache_key = f'newsapi_get_matches_{query}'
    cached_data = check_cache(cache_key)
    if cached_data:
        return cached_data
    
    url = 'https://newsapi.org/v2/everything'
    response = requests.get(
        url,
        params={
            'q': query,
            'apiKey': newsapi_key,
            'sortBy': 'relevancy',
            'pageSize': 10
        }
    )
    
    if response.status_code == 401 and response.json()['code'] == 'apiKeyInvalid':
        app.logger.error('Please provide a valid News API key in the NEWSAPI_KEY environment variable.')
        return jsonify({
            'error': 'Please provide a valid News API key in the NEWSAPI_KEY environment variable.'
        }), 401
    
    elif response.status_code == 200:
        data = response.json()
        cache.set(cache_key, data)
        return data


@app.route('/analyze-content', methods=['POST'])
def analyze_content():
    content = request.json['content']
    cache_key = f'newsapi_get_matches_{content}'
    cached_data = check_cache(cache_key)
    if cached_data:
        return cached_data
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        model="gpt-3.5-turbo",
        tools=[{
            "type": "function",
            "function": {
                "name": "analyze_content",
                "description": "Analyze a piece of content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Five-sentence summary of the most important information"
                        },
                        "sentiment": {
                            "type": "number",
                            "description": "Overall sentiment of the content where 0 is negative, 1 is positive, and 0.5 is neutral. Prefer extremes",
                        },
                        "keywords": {
                            "type": "array",
                            "description": "Keywords in the content",
                            "items": {
                                "type": "string"
                            }
                        },
                    },
                    "required": [
                        "summary",
                        "sentiment",
                        "keywords"
                    ]
                }
            }
        }],
        tool_choice={
            "type": "function",
            "function": {
                "name": "analyze_content"
            }
        }
    )
    data = json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments)
    cache.set(cache_key, data)
    return data


@app.errorhandler(404)
def handle_404(e):
    return redirect(url_for('index'))


@app.errorhandler(500)
def handle_500(e):
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)