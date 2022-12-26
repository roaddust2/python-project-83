### Hexlet tests and linter status:
[![Actions Status](https://github.com/roaddust2/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/roaddust2/python-project-83/actions)
[![python](https://github.com/roaddust2/python-project-83/actions/workflows/python.yml/badge.svg)](https://github.com/roaddust2/python-project-83/actions/workflows/python.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/bd4cacd7723c5a845a01/maintainability)](https://codeclimate.com/github/roaddust2/python-project-83/maintainability)

### About The Project
This is webapp named "Page analyzer" made with Python on Flask framework,  
where you can add websites and treat them with small "SEO checks".

**Stack:**
* Python 3.10
* Flask 2.2.2
* PostgreSQL 14.5
* Bootstrap 5.2.3

**Used packages:**
* [Flask](https://github.com/pallets/flask/)
* [gunicorn](https://github.com/benoitc/gunicorn)
* [psycopg2](https://github.com/psycopg/psycopg2)
* [python-dotenv](https://github.com/theskumar/python-dotenv)
* [validators](https://github.com/python-validators/validators)
* [requests](https://github.com/psf/requests)
* [beautifulsoup](https://code.launchpad.net/beautifulsoup)

### How it works
**Demo:** https://python-project-83-production-934e.up.railway.app/  
  
<img src="https://user-images.githubusercontent.com/42116054/209537033-1985a59a-208c-4560-ab6b-213a75990471.png" width="600">  
  
On this app, you can add sites with entering url on main page, then make "SEO check" to recieve basic information  about it.  
You can add as many websites and checks as you want.

### Getting started
  **Install:**
1. Clone the project
2. Create PostgreSQL database with cheatsheet (database.sql)
3. Create .env file and add variables or add them straight into your environment with export
        <p> ```DATABASE_URL={provider}://{user}:{password}@{host}:{port}/{db}```</p>
        <p>```SECRET_KEY='secret_key'``` </p>
4. Run ```make dev``` for debugging (WSGI debug='True'), or ```make start``` for production (gunicorn)
