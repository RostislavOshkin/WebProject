from flask import Flask
from flask import render_template
import sqlite3

app = Flask(__name__)

host = '127.0.0.1'
port = 8080


@app.route('/')
@app.route('/index')
def index():
    user = "Гость"
    return render_template('index.html', title='Главная страница',
                           username=user)


@app.route('/search')
def search():
    con = sqlite3.connect('db.db')
    req = f"""Select name, id_person, description, price, data, id_files from adverts"""
    cur = con.cursor()
    ans = cur.execute(req).fetchall()
    con.close()
    return render_template('searchT.html', title='Поиск', adverts=ans)


@app.route('/configuration')
def configuration():
    return render_template('configurationT.html', title='Настройки')


@app.route('/profile/<id>')
def profile(id):
    return render_template('profileT.html', title='Поиск', id=id)


def create():
    try:
        open('db.db', mode='r')
    except Exception:
        open('db.db', mode='w').close()
        con = sqlite3.connect('db.db')
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS adverts(
       id INT PRIMARY KEY,
       name TEXT,
       id_person INT,
       description TEXT,
       price TEXT, 
       data DATE, 
       id_files INT);
    """)
        con.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
       id INT PRIMARY KEY,
       name TEXT,
       description TEXT,
       address TEXT,  
       password TEXT);
    """)
        con.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS files(
           id INT PRIMARY KEY,
           name TEXT,
           file BLOB);
        """)
        con.commit()
        con.close()


if __name__ == '__main__':
    app.run(port=port, host=host)
