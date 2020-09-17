import parser

from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'My simply application'

menu = ['Home', 'links', 'about']
categories = ['business','technology', 'entertainment',
             'sports', 'science', 'health']

@app.route('/')
def index():
    query = None
    if request.args:
        query = request.args['query']
    data = parser.request_api(query=query)
    articles = data['articles']
    if not articles:
        flash(f'Not found any results for {query}')
    return render_template('base.html', menu=menu,
                           categories=categories,
                           articles=articles)

@app.route('/topics/<topic>/')
def add_category(topic):
    query = request.form.get('query')
    data = parser.request_api(cat=topic, query=query)
    articles = data['articles']
    return render_template('template.html', menu=menu,
                           categories=categories,
                           articles=articles)

@app.context_processor
def utility_processor():
    def send_data(url):
        with app.test_request_context(f'/?redirect={url}') as ctx:
            read_url(url)


def read_url(url):
    data = parser.parse_url(url)
    return render_template('article.html', menu=menu,
                           categories=categories,
                           data=data)


# if __name__ == '__main__':
app.jinja_env.filters['truncate_text'] = parser.truncate
app.run('192.168.0.8', 8000, debug=True)
