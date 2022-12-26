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
from validators import url as valid
from urllib.parse import urlparse
import page_analyzer.db as db
import page_analyzer.check as check

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


def normalize_url(url):
    url = urlparse(url)
    return url._replace(
        path='',
        params='',
        query='',
        fragment='').geturl()


@app.errorhandler(404)
def page_not_found(e):
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

    if exists[0]:
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('url_get', id=exists[1]))

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
    response = check.get_status_code(url['name'])
    if response:
        page = check.get_data(url['name'])
        db.add_check({
                'id': id,
                'status_code': response,
                'h1': page['h1'],
                'title': page['title'],
                'content': page['content']})
        flash('Страница успешно проверена', 'alert-success')
        return redirect(url_for('url_get', id=id))
    flash('Произошла ошибка при проверке', 'alert-danger')
    return redirect(url_for('url_get', id=id))
