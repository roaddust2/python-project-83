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
import page_analyzer.db as db
import page_analyzer.check as check

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    rows = db.get_urls()
    return render_template(
        'urls.html',
        urls=rows
    )


@app.post('/urls')
def url_post():
    input = request.form.to_dict()
    result = db.add_url(input['url'])

    match result:
        case 'IncorrectUrl':
            flash('Некорректный URL', 'alert-danger')
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'index.html',
                url=input['url'],
                messages=messages
            )
        case 'UniqueViolation':
            flash('Страница уже существует', 'alert-info')
            id = db.find_url_by_name(input['url']).get('id')
            return redirect(url_for('url_get', id=id))
        case _:
            flash('Страница успешно добавлена', 'alert-success')
            return redirect(url_for('url_get', id=result))


@app.get('/urls/<int:id>')
def url_get(id):
    row = db.find_url_by_id(id)
    messages = get_flashed_messages(with_categories=True)
    checks = db.get_checks(id)
    return render_template(
        'url.html',
        url=row,
        checks=checks,
        messages=messages
    )


@app.post('/urls/<int:id>/checks')
def url_check(id):
    row = db.find_url_by_id(id)
    response = check.get_status_code(row['name'])
    if response:
        page = check.get_data(row['name'])
        db.add_check(
            id,
            response,
            page['h1'],
            page['title'],
            page['content'])
        return redirect(url_for('url_get', id=id))
    flash('Произошла ошибка при проверке', 'alert-danger')
    return redirect(url_for('url_get', id=id))
