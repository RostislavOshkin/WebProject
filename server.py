import re
import os
import sqlite3
from datetime import timedelta

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api

from data import db_session, users_resources, adverts_resources
from data.users import User
from data.adverts import Advert
from data.config import Config
from data.files import File

from forms.loginform import LoginForm
from forms.advertform import AdvertForm
from forms.register import RegisterForm
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
app.config['UPLOAD_FOLDER'] = 'local'
login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app, catch_all_404s=True)


# главная страница
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html', title='Главная страница',
                           user=current_user)


# инициализация поиска
@app.route('/', methods=['POST'])
@app.route('/index', methods=['POST'])
@app.route('/search/<text>', methods=['POST'])
@app.route('/configuration', methods=['POST'])
@app.route('/profile', methods=['POST'])
def start_search(text=''):
    if "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    if 'btn' in request.form and request.form['btn'] == 'advertsPRF#':
        return redirect(f'/profile/adverts')
    if 'btn' in request.form and request.form['btn'] == 'configsPRF#':
        db_sess = db_session.create_session()
        i = db_sess.query(Config).filter(Config.person_id == current_user.id).first()
        i.search = not i.search
        db_sess.add(i)
        db_sess.commit()
    return redirect(request.full_path[:-1])


# поиск
@app.route('/search/<text>', methods=['GET'])
def search(text):
    search_text = re.sub(r'\W', '', text.lower())
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        ans = db_sess.query(Advert).filter(Advert.for_search.ilike(f'%{search_text}%'))
    elif db_sess.query(Config).filter(Config.person_id == current_user.id)[0].search:
        ans = db_sess.query(Advert).filter(Advert.name.ilike(f'%{search_text}%'))
    else:
        ans = db_sess.query(Advert).filter(Advert.for_search.ilike(f'%{search_text}%'))
    return render_template('searchT.html', title='Поиск', adverts=ans, user=current_user, search=text)


# открытие прикреплённых к объявлению файлов
@app.route('/files/<id>', methods=['GET'])
@app.route('/profile/files/<id>', methods=['GET'])
def get_files(id):
    db_sess = db_session.create_session()
    if 'None' not in id:
        ans = db_sess.query(File).filter(File.advrt_id == int(id))
    else:
        ans = None
    if ans is None:
        return "<h1>Прикреплённых файлов нет.</h1>"
    return render_template('filesGetT.html', title='Файлы', files=ans, user=current_user)


# скачивание файла
@app.route('/file/<id>', methods=['GET'])
def get_file(id):
    db_sess = db_session.create_session()
    ans = db_sess.query(File.file).filter(File.id == int(id[0]))
    return ans[0][0]


# настройки
@app.route('/configuration', methods=['GET'])
def configuration():
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        return "<h1>Необходимо войти, чтобы пользоваться этим.</h1>"
    bolean = db_sess.query(Config).filter(Config.person_id == current_user.id)[0].search
    return render_template('configurationT.html', title='Настройки', user=current_user, bolean=bolean)


# открытие профиля
@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profileT.html', title='Поиск', user=current_user)


# открытие объявлений
@app.route('/profile/adverts', methods=['GET', "POST"])
def adverts():
    btn_command, id = '', ''
    db_sess = db_session.create_session()
    if request.method == 'POST' and "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    elif request.method == 'POST' and 'btn' in request.form:
        btn_command, id = request.form['btn'].split()
    if btn_command == 'del':
        return redirect(f'/profile/adverts/delete_advert/{id}')
    if btn_command == '/':
        return redirect(f'/profile/adverts/files/download/{id}/{current_user.id}')
    if btn_command == 'update':
        return redirect(f'/profile/adverts/update_advert/{id}')
    lst = db_sess.query(Advert).filter(Advert.id_person == current_user.id)
    return render_template('advertT.html', title='Ваши объявления', user=current_user, advrts=lst,
                           btn_command=btn_command)


@app.route('/profile/adverts/files/download/<id_advrt>/<id_person>', methods=['GET', "POST"])
def selecting_files_in_advert(id_advrt, id_person):
    if request.method == 'GET':
        return render_template('fileSelectT.html', title='Загрузка файлов', user=current_user)
    if current_user.id == int(id_person):
        saver(request.files['file'])
        db_sess = db_session.create_session()
        filename = secure_filename(request.files['file'].filename)
        file = File(advrt_id=id_advrt, name=filename, file=open(f'local/{filename}', mode='br').read())
        db_sess.add(file)
        db_sess.commit()
        poper(filename)
    return redirect(f'/profile/adverts')


def saver(file):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'bmp'}
    filename = file.filename
    if '.' in filename and filename.split('.')[1].lower() in ALLOWED_EXTENSIONS:
        # безопастно извлекаем имя файла
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        print("success saver")


def poper(filename):
    if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("success poper")


# создать новое объявление
@app.route('/profile/adverts/new_advert', methods=['GET', 'POST'])
def new_advert():
    if request.method == 'POST' and "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    form = AdvertForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        con = sqlite3.connect('db.db')
        cur = con.cursor()
        advert = Advert(name=form.name.data, id_person=current_user.id, description=form.description.data,
                        price=form.price.data,
                        id_files=cur.execute(f"""Select MAX(id_files) + 1 From adverts""").fetchone()[0],
                        for_search=re.sub(r'\W', '', (form.name.data + form.description.data).lower()))
        con.close()
        db_sess.add(advert)
        db_sess.commit()
        return redirect('/profile/adverts')
    advert = Advert(name='', id_person='', description='', price='', for_search='')
    return render_template('advertformT.html', title='Новое объявление', form=form, user=current_user, advert=advert)


# изменение объявления
@app.route('/profile/adverts/update_advert/<id>', methods=['GET', 'POST'])
def update_advert(id):
    if request.method == 'POST' and "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    form = AdvertForm()
    db_sess = db_session.create_session()
    advert = db_sess.query(Advert).filter(Advert.id == id).first()
    if form.validate_on_submit():
        advert.name = form.name.data
        advert.description = form.description.data
        advert.price = form.price.data
        advert.for_search = re.sub(r'\W', '', (form.name.data + form.description.data).lower())
        db_sess.commit()
        return redirect('/profile/adverts')
    return render_template('advertformT.html', title='Изменить объявление', form=form, user=current_user,
                           advert=advert)


# удалить объявление
@app.route('/profile/adverts/delete_advert/<id>', methods=['GET', 'POST'])
def delete_advert(id):
    db_sess = db_session.create_session()
    del_advert = db_sess.query(Advert).filter(Advert.id == id).first()
    if request.method == 'POST':
        db_sess.delete(del_advert)
        db_sess.commit()
        return redirect('/profile/adverts')
    return render_template('deletion_confirmation.html', text=f"объявление \"{del_advert.name}\"", user=current_user)



# вход в систему
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
            if not db_sess.query(Config).filter(Config.person_id == current_user.id).count():
                config = Config(person_id=user.id)
                db_sess.add(config)
                db_sess.commit()
            return redirect("/")
        return render_template('loginT.html', title='Авторизация', message="Неправильный логин или пароль",
                               form=form, user=current_user)
    return render_template('loginT.html', title='Авторизация', form=form, user=current_user)


# выход из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


# регистрация пользователей
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
        user = User(name=form.name.data,
                    address=form.address.data,
                    description=form.description.data,
                    communication=form.communication.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registerT.html', title='Регистрация', form=form, user=current_user)


# удаление пользователя
@app.route('/profile/delete_profile', methods=['GET', 'POST'])
def delete_profile():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        db_sess.delete(user)
        db_sess.commit()
        return logout()
    return render_template('deletion_confirmation.html', text="данный профиль", user=current_user)


if __name__ == '__main__':
    db_session.global_init("db.db")

    # для списка пользователей
    api.add_resource(users_resources.UsersListResource, '/api/users')
    # для одного пользователя
    api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')

    # для списка объявлений
    api.add_resource(adverts_resources.AdvertsListResource, '/api/adverts')
    # для одного объявления
    api.add_resource(adverts_resources.AdvertsResource, '/api/adverts/<int:advert_id>')

    app.run()
