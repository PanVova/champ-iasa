from newsapi import NewsApiClient
from flask import Flask, render_template, jsonify

# Init
newsapi = NewsApiClient(api_key='276da18e0b614daea3b660c8480f62a4')
app = Flask("web")


#Constants
languages = ['ar', 'de', 'en', 'es', 'fr', 'he', 'it', 'nl', 'no', 'pt', 'ru', 'sv', 'ud', 'zh']

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/languages', methods=['GET'])
def get_languages():
    return  jsonify(languages)

def get_articles_by_query_and_language(query, language):
    jsonResponse = newsapi.get_everything(
        q=query,
        language=language
    )
    return jsonResponse['articles']

if __name__ == "__main__":
    app.run(debug=True)