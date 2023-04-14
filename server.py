from flask import Flask
from flask import render_template

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
    return render_template('searchT.html', title='Поиск')


@app.route('/configuration')
def configuration():
    return render_template('configurationT.html', title='Настройки')


@app.route('/profile/<id>')
def profile(id):
    return render_template('profileT.html', title='Поиск', id=id)


if __name__ == '__main__':
    app.run(port=port, host=host)
