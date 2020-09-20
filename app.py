import parser

from flask import Flask, render_template, request, flash, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'My simply application'

menu = ['Home', 'links', 'about']
categories = ['business', 'technology', 'entertainment',
              'sports', 'science', 'health']


@app.route('/')
def index():
    query = None
    if request.args.get('url'):
        url = request.args['url']
        data = parser.parse_url(url)
        print(data)
        return f'<div>{data}</div>'
    else:
        if request.args.get('query'):
            query = request.args['query']
        data = parser.request_api(query=query)
        articles = data['articles']
        if not articles:
            flash(f'Not found any results for {query}')
        return render_template('index.html', menu=menu,
                               categories=categories,
                               articles=articles)

@app.route('/topics/<topic>/')
def add_category(topic):
    query = request.form.get('query')
    data = parser.request_api(cat=topic, query=query)
    articles = data['articles']
    return render_template('index.html', menu=menu,
                           categories=categories,
                           articles=articles)


@app.route('/articles/<url>/')
def read_url(url):
    # if request.args.get('url'):
    #     url = request.args['url']
    data = parser.parse_url(url)
    print(data)
    return f'<div>{data}</div>'


# if __name__ == '__main__':
app.jinja_env.filters['truncate_text'] = parser.truncate
app.run(debug=True)
