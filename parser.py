import re
import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

def request_api(cat=None, query=None):
    import newsapi
    newsapi = newsapi.NewsApiClient(api_key='fd1e2db0438341cbbd62315ed0db78bd')
    data = newsapi.get_top_headlines(q=query, language='ru', country='ru', category=cat)
    return data

def format_links(d, node):
    if d[0] in node["src"]:
        img = f'<img src={node["src"]}>'
    else:
        img = f'<img src={d[0]}{node["src"]}>'
    return img

def parse_url(url=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    d = re.search(r'\w+:\/\/[\w\d\-._]+', url)
    html = str()
    src = str()
    s1 = True
    s2 = True
    body = soup.body
    for ch in body.descendants:
        try:
            if re.search(r'h[2-6]', ch.name) and not ch.get('class'):
                html += str(ch)

            if ch.name == 'img':
                if re.search(r'menu|line*|hidden|none', str(ch.attrs)):
                    s1 = False
                    continue
                else:
                    s1 = True
                for parent in ch.parents:
                    if re.search(r'menu|line*|hidden|none', str(parent.attrs)):    
                        s1 = False
                        break
                    else:
                        s1 = True
                if s1:
                    html += format_links(d, ch)            
            if ch.name == 'p' and not ch.get('class'):
                print(ch)
                for element in ch.children:
                    if isinstance(element, str):
                        html += f'<p>{element}</p>'
                    if element.name == 'a':
                        html += format_links(d, element)
            if ch.name == 'ul' and not ch.get('class'):
                html += '<ul>'
                for element in ch.children:
                    if not element.get('class'):
                        html += str(element)
        except:
            continue
    html = re.sub(r'[\[\]]', '', html)
    return html

def truncate(text, n):
    text = text.split('.')[0]
    if len(text) >= n:
        text = text[:130] + '...'
    else:
        text = text + '.'
    return text
