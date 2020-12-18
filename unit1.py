import binascii
import io
import re
import os
import subprocess
import traceback

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import soupsieve as sv
from PIL import Image
import lxml


def request_api(cat=None, query=None):
    import newsapi
    newsapi = newsapi.NewsApiClient(api_key='fd1e2db0438341cbbd62315ed0db78bd')
    data = newsapi.get_top_headlines(q=query, language='ru', country='ru', category=cat)
    return data

def get_articles(soup):
    slc1 = 'article:has( p)'
    a1 = soup.select_one(slc1)
    slc2 = 'div:has(> [itemprop="articleBody"]:has(> p))'
    a2 = soup.select_one(slc2)
    headers = 'h1,h2,h3,h4,h5,h6'
    if a1:
        return soup.select(f'{slc1} *')
    elif a2:
        return soup.select(f'''{slc2} > :is(div[itemprop="articleBody"], 
                           div[class*="header"]) *''')

def parse_url(url=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    d = re.search(r'\w+:\/\/[\w\d\-._]+', url)
    html = str()
    src = str()
    ref = src
    s1 = True
    s2 = True
    s3 = True
    articles = get_articles(soup)
    for ch in articles:
        try:
            if ch.string and re.search(r'h[1-6]', str(ch.name)):
                html += str(ch)

            if ch.name == 'div' and ch.string:
                html += f'<div>{str(ch.string)}</div>'
            if ch.name == 'ul' and not ch.get('class'):
                html += '<ul>'
                for element in ch.children:
                    if element.name == 'li' and element.string and not element.get('class'):
                        html += str(element)
            if ch.name == 'blockquote':
                html += str(ch)
            if ch.name == 'p':
                a = None
                s = str()
                string = str()
                p_tags = ch.contents
                print(p_tags)
                for i in range(len(p_tags)):
                    if isinstance(p_tags[i], Tag):
                        if p_tags[i].get('href'):
                            if d[0] in p_tags[i]['href']:
                               pass
                            else:
                                match = re.compile(r'\w+:\/\/[\w\-\/\.]+').\
                                    search(p_tags[i]['href'])
                                if match and match[0] != d[0]:
                                    pass
                                else:
                                    p_tags[i]['href'] = f'{d[0]}{p_tags[i]["href"]}'
                                    ch.insert(i, p_tags[i])
                        elif p_tags[i].name == 'b':
                            ch.clear(p_tags[i])
                print(p_tags)
                html += str(ch)
            if ch.name == 'img':
                print(ch.name, ch.attrs)
                w = str()
                h = str()
                match = re.search(r'\w+:\/\/\w+.[\w\d\-_]+\.[\w]+', str(ch))
                if ch.get('width'):
                    w = str(ch['width'])
                if ch.get('height'):
                    h = str(ch['height'])
                if match:
                    m = re.search(r'(\w+:\/\/[\w\-\.]+[\w\d\-_]+\.[\/\w]+.(?:jpe?g|png))', str(ch))
                    ref = m.group(0)
                    node = f'<img src="{ref}" class="article_img" width={w}, height={h}>'
                else:
                    match = re.search(r'[\w\/ \-\.]*', str(ch['src']))
                    ref = f'{d[0]}{match[0]}'
                    print(ref)
                    node = f'<img src="{ref}" class="article_img" width={w} height={h}>'
                html += node
        except:
            print(traceback.format_exc())
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
