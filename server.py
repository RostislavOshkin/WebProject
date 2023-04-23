import re

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from data import db_session
from data.users import User
from data.adverts import Advert
from forms.advertform import AdvertForm
from data.files import File
from forms.loginform import LoginForm
from forms.register import RegisterForm

from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)

host = '127.0.0.1'
port = 8080


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html', title='Главная страница',
                           user=current_user)


@app.route('/', methods=['POST'])
@app.route('/index', methods=['POST'])
@app.route('/search/<text>', methods=['POST'])
@app.route('/configuration', methods=['POST'])
@app.route('/profile', methods=['POST'])
def start_search(text=''):
    if "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    return redirect(request.full_path[:-1])


@app.route('/search/<text>', methods=['GET'])
def search(text):
    search_text = re.sub(r'\W', '', text.lower())
    db_sess = db_session.create_session()
    ans = db_sess.query(Advert).filter(Advert.for_search.ilike(f'%{search_text}%'))
    return render_template('searchT.html', title='Поиск', adverts=ans, user=current_user, search=text)


@app.route('/files/<id>', methods=['GET'])
@app.route('/profile/files/<id>', methods=['GET'])
def get_files(id):
    db_sess = db_session.create_session()
    ans = db_sess.query(File).filter(File.advrt_id == int(id[0]))
    return render_template('filesGetT.html', title='Поиск', files=ans, user=current_user)


@app.route('/file/<id>', methods=['GET'])
def get_file(id):
    db_sess = db_session.create_session()
    ans = db_sess.query(File.file).filter(File.id == int(id[0]))
    return ans[0][0]


@app.route('/configuration', methods=['GET'])
def configuration():
    return render_template('configurationT.html', title='Настройки', user=current_user)


@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profileT.html', title='Поиск', user=current_user)


@app.route('/profile/adverts', methods=['GET', "POST"])
def adverts():
    db_sess = db_session.create_session()
    btn_command = ''
    if request.method == 'POST' and "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    elif request.method == 'POST' and 'btn' in request.form:
        btn_command, id = request.form['btn'].split()

    if btn_command == 'del':
        lst = db_sess.query(Advert).filter(Advert.id == id).first()
        db_sess.delete(lst)
        db_sess.commit()
    db_sess = db_session.create_session()
    lst = db_sess.query(Advert).filter(Advert.id_person == current_user.id)
    return render_template('advertT.html', title='Ваши объявления', user=current_user, advrts=lst,
                           btn_command=btn_command)


@app.route('/profile/adverts/new_advert', methods=['GET', 'POST'])
def new_advert():
    if request.method == 'POST' and "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    form = AdvertForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        advert = Advert(name=form.name.data, id_person=current_user.id, description=form.description.data,
                        price=form.price.data,
                        for_search=re.sub(r'\W', '', (form.name.data + form.description.data).lower()))
        db_sess.add(advert)
        db_sess.commit()
        return redirect('/profile/adverts')
    return render_template('advertformT.html', title='Новое объявление', form=form, user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.address == form.address.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('loginT.html', title='Авторизация', message="Неправильный логин или пароль",
                               form=form, user=current_user)
    return render_template('loginT.html', title='Авторизация', form=form, user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registerT.html', title='Регистрация', form=form, message="Пароли не совпадают",
                                   user=current_user)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.address == form.address.data).first():
            return render_template('registerT.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть", user=current_user)
        user = User(name=form.name.data, address=form.address.data, description=form.description.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registerT.html', title='Регистрация', form=form, user=current_user)


if __name__ == '__main__':
    db_session.global_init("db.db")
    app.run(port=port, host=host)
