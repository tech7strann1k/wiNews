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

headers = 'h1,h2,h3,h4,h5,h6'

def get_articles(soup):
    slc1 = 'article:has( p)'
    a1 = soup.select_one(slc1)
    slc2 = 'div:has(> [itemprop="articleBody"]:has( p, div, a))'
    a2 = soup.select_one(slc2)
    slc3 = '''div:is([class*="article"], [class*="head"], [class^="article__header"]),
        div[class^="article_block"]:has(div[class^="article__text"])'''
    a3 = soup.select(slc3)
    if a1:
        return sv.select(slc1, soup)
    elif a2:
        s1 = sv.select(f'{slc2} [itemprop="headline"], [itemprop="articleBody"] :has(>p)', soup)
        return s1
    elif a3:
        return sv.select(f'''div:is([class*="article"], 
            [class*="head"], [class^="article__header"])''', soup)
    else:
        return sv.select(f'''#div_postbody *, :has(#div_postbody) > :is({headers}), 
            [itemprop="headline"], .content *''', soup)

def get_href(d, ch):
    ch_tags = ch.contents
    for i in range(len(ch_tags)):
        if isinstance(ch_tags[i], Tag):
            if ch_tags[i].get('href'):
                if re.search(r'<img[\S ]+', str(ch_tags[i].contents)):
                    ch_tags[i] = None
                if d[0] in ch_tags[i]['href']:
                    pass
                else:
                    match = re.compile(r'\w+:\/\/[\w\-\/\.]+'). \
                        search(ch_tags[i]['href'])
                    if match and match[0] != d[0]:
                        pass
                    else:
                        ch_tags[i]['href'] = f'{d[0]}{ch_tags[i]["href"]}'
                        ch.insert(i, ch_tags[i])
            if re.compile(r'h[1-6]|b').search(ch_tags[i].name):
                ch_tags[i] = None

    return ch

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
    print(articles[:2])
    for i in articles[:2]:
        try:
            if re.search(r'h[1-6]', str(i.name)):
               html += str(i)
            for ch in i.descendants:
                if ch.name == 'div':
                    if ch.attrs == {} or re.compile('jsx|title|text').search(str(ch.attrs)):
                        html += str(get_href(d, ch))
                if re.compile('ul|ol').search(str(ch.name)) and not ch.get('class'):
                    html += '<ul>'
                    for element in ch.children:
                        if element.name == 'li' and element.string and not element.get('class'):
                            html += str(element)
                if ch.name == 'blockquote':
                    html += str(ch)
                if ch.name == 'p' and ch.parent.name != 'blockquote':
                    html += str(get_href(d, ch))
                if ch.name == 'img':
                    w = str()
                    h = str()
                    match = re.search(r'\w+:\/\/\w+.[\w\d\-_]+\.[\w]+', str(ch))
                    try:
                        if ch.get('width'):
                            w = str(i['width'])
                        if ch.get('height'):
                            h = str(i['height'])
                    except KeyError:
                        pass
                    if match:
                        m = re.search(r'\w+:\/\/[\w\-\.]+[\/\w\-]+[\w\/\.]+', str(ch))
                        ref = m.group(0)
                        node = f'<img src="{ref}" class="article_img" width={w}, height={h} alt="">'
                    else:
                        match = re.search(r'[\w\/ \-\.]*', str(ch['src']))
                        ref = f'{d[0]}{match[0]}'
                        node = f'<img src="{ref}" class="article_img" width={w} height={h} alt="">'
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
