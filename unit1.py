import binascii
import io
import re
import os
import subprocess
import traceback

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from io import BytesIO
import soupsieve as sv
from PIL import Image
import lxml


def request_api(cat=None, query=None):
    import newsapi
    newsapi = newsapi.NewsApiClient(api_key='fd1e2db0438341cbbd62315ed0db78bd')
    data = newsapi.get_top_headlines(q=query, language='ru', country='ru', category=cat)
    return data

headers = '>h1,>h2,>h3,>h4,>h5,>h6'
headers_ = headers.replace('>', '')

def get_articles(soup):
    slc1 = f'[class*="topic__content"]'
    a1 = sv.select(slc1, soup)
    slc2 = '''[class*="article"], [class*="head"],
           header, [itemprop="articleBody"]:has( p, div, a), [class*="article__header"],
           div[class^="article_block"]:has(div[class^="article__text"])'''
    a2 = sv.select(slc2, soup)
    if len(a1) > 1:
        print('a1')
        s1 = sv.iselect(f'''{slc1} img, [class*="article__header"] *, [itemprop="headline"], 
        [itemprop="articleBody"]:has(>p, >img) *, [itemprop="articleBody"] :has(>p,>img) *''', soup)
        return s1
    if len(a2) > 1:
        print('a2')
        s2 = sv.iselect(f'''header:has({headers}) > * , [class*=article__header] *, [itemprop=headline], [itemprop="articleBody"]:has(>p, >img) *,  
            [itemprop="articleBody"] :has(>p,>img) *''', soup)
        return s2
    else:
        print('a4')
        return sv.iselect(f'''#div_postbody *, :has(#div_postbody) > :is({headers}), 
            [itemprop="headline"], .content *''', soup)

def get_href(d, ch):
    try:
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
                if re.compile(r'h[1-6]|b|img').search(ch_tags[i].name):
                    ch_tags[i] = None
    except TypeError:
        pass
    return ch

def parse_url(url=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    d = re.search(r'\w+:\/\/[\w\d\-._]+', url)
    html = str()
    string = None
    articles = get_articles(soup)
    for ch in articles:
        try:
            if isinstance(ch, Tag):
                if re.search(r'h[1-6]', str(ch.name)):
                    html += str(ch)
                if ch.name == 'div':
                    try:
                        if ch.attrs == {} or re.compile('jsx|title|text').search(str(ch.attrs)):
                            html += str(get_href(d, ch))
                    except IndexError:
                        pass
                if ch.find('a', class_=True):
                    ch.clear()
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
                    pattern = r"\w+:\/\/[\w\d\/-_\.]+\b"
                    if ch.get('srcset'):
                        match = re.search(pattern, ch.get('srcset'))
                        string = match[0]
                        print(string)
                    elif ch.get('src'):
                        match = re.search(pattern, ch.get('src'))
                        string = match[0]
                    try:
                        if ch.get('width'):
                            w = str(ch['width'])
                        if ch.get('height'):
                            h = str(ch['height'])
                    except KeyError:
                        pass
                    if string:
                        ref = string
                        # response = requests.get(ref)
                        # image = Image.open(BytesIO(response.content))
                        # width = image.width
                        # height = image.height
                        # if width >= 480:
                        if ref not in html:
                            html += f'<img src="{ref}" class="article_img" alt="">'
                        else:
                            continue
                    else:
                        match = re.search(r'src="([\w\/ \-\.]+)"', str(ch))
                        ref = f'{d[0]}{match[1]}'
                        # print(match[0])
                        # response = requests.get(ref)
                        # print(response.url)
                        # image = Image.open(BytesIO(response.content))
                        # width = image.width
                        # height = image.height
                        # if width >= 480:
                        html += f'<img src="{ref}" class="article_img" alt="">'
                        # else:
                        #     continue
        except:
            print(traceback.format_exc())
            continue

    html = re.sub(r'[\[\]]', '', html)
    print(html)
    return html

def truncate(text, n):
    text = text.split('.')[0]
    if len(text) >= n:
        text = text[:130] + '...'
    else:
        text = text + '.'
    return text
