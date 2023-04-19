from flask import Flask
from flask import render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from data.adverts import Advert
from forms.loginform import LoginForm
from data import db_session
from data.users import User
from forms.register import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

host = '127.0.0.1'
port = 8080


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Главная страница',
                           user=current_user)


@app.route('/search')
def search():
    db_sess = db_session.create_session()
    ans = db_sess.query(Advert).all()  # filter(Advert.name.like('%'))
    print(ans)
    return render_template('searchT.html', title='Поиск', adverts=ans, user=current_user)


@app.route('/configuration')
def configuration():
    return render_template('configurationT.html', title='Настройки', user=current_user)


@app.route('/profile/<id>')
def profile(id):
    return render_template('profileT.html', title='Поиск', id=id, user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.address == form.address.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('loginT.html', message="Неправильный логин или пароль", form=form, user=current_user)
    return render_template('loginT.html', title='Авторизация', form=form, user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registerT.html', title='Регистрация', form=form, message="Пароли не совпадают", user=current_user)
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
