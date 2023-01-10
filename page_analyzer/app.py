import os
from flask import (
    Flask,
    render_template,
    url_for,
    redirect,
    request,
    flash,
    get_flashed_messages
)
from dotenv import load_dotenv
import requests
from validators import url as valid
from urllib.parse import urlparse
import page_analyzer.db as db
from bs4 import BeautifulSoup
import logging

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Logging configuration
logging.basicConfig(
    filename='logs.log',
    filemode='w',
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )

logger = logging.getLogger(__name__)


def normalize_url(url):
    url = urlparse(url)
    return url._replace(
        path='',
        params='',
        query='',
        fragment='').geturl()


@app.errorhandler(404)
def page_not_found():
    return render_template('errors/404.html'), 404


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    urls = db.get_urls()
    return render_template(
        'urls.html',
        urls=urls
    )


@app.post('/urls')
def url_post():
    input = request.form.to_dict()
    url = input['url']

    if not valid(url):
        flash('Некорректный URL', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            url=url,
            messages=messages), 422

    url = normalize_url(url)
    exists = db.exist_url(url)

    if exists:
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('url_get', id=db.find_url(url).id))

    result = db.add_url(url)

    match result:
        case None:
            flash('Произошла ошибка', 'alert-danger')
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'index.html',
                url=url,
                messages=messages), 500
        case _:
            flash('Страница успешно добавлена', 'alert-success')
            return redirect(url_for('url_get', id=result))


@app.get('/urls/<int:id>')
def url_get(id):
    url = db.find_url(id)
    checks = db.get_checks(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'url.html',
        url=url,
        checks=checks,
        messages=messages
    )


@app.post('/urls/<int:id>/checks')
def url_check(id):
    url = db.find_url(id)
    try:
        response = requests.get(url.name)
        response.raise_for_status()
        page = get_page(url.name)
        db.add_check({
            'id': id,
            'status_code': response.status_code,
            'h1': page['h1'],
            'title': page['title'],
            'content': page['content']})
        flash('Страница успешно проверена', 'alert-success')
        return redirect(url_for('url_get', id=id))
    except Exception as err:
        logging.error(err)
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('url_get', id=id))


def get_page(url: str) -> dict:
    """
    Function that parses page and returns content in a dict
    Keyword arguments:
        url : str - valid url for example 'https://www.example.com'
    """
    page_text = {
        'h1': '',
        'title': '',
        'content': ''
    }
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.h1
    title = soup.title
    content = soup.find(
        "meta", attrs={'name': 'description'})

    page_text.update(
        {'h1': h1.get_text()}
    ) if h1 is not None else page_text.setdefault('h1', '')
    page_text.update(
        {'title': title.get_text()}
    ) if title is not None else page_text.setdefault('title', '')
    page_text.update(
        {'content': content["content"]}
    ) if content is not None else page_text.setdefault('content', '')
    return page_text
