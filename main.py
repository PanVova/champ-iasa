from newsapi import NewsApiClient

# Init
newsapi = NewsApiClient(api_key='276da18e0b614daea3b660c8480f62a4')


# /v2/everything
all_articles = newsapi.get_everything(q='bitcoin',
                                      sources='bbc-news,the-verge',
                                      domains='bbc.co.uk,techcrunch.com',
                                      from_param='2024-01-09',
                                      to='2024-02-09',
                                      language='en',
                                      sort_by='relevancy',
                                      page=2)

# /v2/top-headlines/sources
sources = newsapi.get_sources()
print(sources)