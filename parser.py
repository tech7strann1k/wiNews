import re

import requests
from bs4 import BeautifulSoup


def request_api(cat=None, query=None):
    import newsapi
    newsapi = newsapi.NewsApiClient(api_key='fd1e2db0438341cbbd62315ed0db78bd')
    data = newsapi.get_top_headlines(q=query, language='ru', country='ru', category=cat)
    return data

def parse_url(url=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html5lib')
    html = str()
    for i in soup.find_all(["p", "ul", "img", "a", re.compile("h[2-6]")], class_=False):
        html += str(i)
    html = re.sub(r'[\[\]]', '', html)
    return html

def truncate(text, n):
    text = text.split('.')[0]
    if len(text) >= n:
        text = text[:130] + '...'
    else:
        text = text + '.'
    return text
