import re
import os
import shutil
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

# PY2 = sys.version_info[0] == 2 - проверка версии Python
# print(sys.version_info[0])

text_type = str
_windows_device_files = (
    "CON",
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "LPT1",
    "LPT2",
    "LPT3",
    "PRN",
    "NUL",
)
_filename_strip_re = re.compile(r"[^A-Za-zа-яА-ЯёЁ0-9_.-]")


def secure_filename(filename: str) -> str:
    if isinstance(filename, text_type):
        from unicodedata import normalize
        filename = normalize("NFKD", filename)

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    filename = str(_filename_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )

    if (
            os.name == "nt"
            and filename
            and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = f"_{filename}"

    return filename


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
app.config['UPLOAD_FOLDER'] = 'local'
login_manager = LoginManager()
login_manager.init_app(app)
# Create the API
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
@app.route('/files/<text>', methods=['POST'])
@app.route('/profile/files/<text>', methods=['POST'])
@app.route('/advert/<text>', methods=['POST'])
@app.route('/profile/vp/<text>', methods=['POST'])
@app.route('/help', methods=['POST'])
@app.route('/about_developers', methods=['POST'])
def start_search(text=''):
    if "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    if 'btn' in request.form and 'StartChat' in request.form['btn']:
        _temp = request.form['btn'].split()
        return redirect(f'/pre-chat/{_temp[1]}/{_temp[2]}')
    if 'btn' in request.form and request.form['btn'] == 'configsPRF#':
        db_sess = db_session.create_session()
        i = db_sess.query(Config).filter(Config.person_id == current_user.id).first()
        i.search = not i.search
        db_sess.add(i)
        db_sess.commit()
    if 'messg' in request.form:
        f_last = ''
        if os.path.isfile(f"notsystemfiles/quests/{current_user.id}"):
            f_last = open(f"notsystemfiles/quests/{current_user.id}", mode='r', encoding='utf8').read()
        f = open(f"notsystemfiles/quests/{current_user.id}", mode='w', encoding='utf8')
        f.write(f_last + '\n\n' + request.form["messg"])
        f.close()
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


# descrAdvrt
@app.route('/advert/<id>', methods=['GET'])
def advert_descr(id):
    db_sess = db_session.create_session()
    adv = db_sess.query(Advert).filter(Advert.id == int(id))
    return render_template('descriptionAdvertT.html', title='Объявление', advert=adv[0], user=current_user)


# открытие прикреплённых к объявлению файлов
@app.route('/files/<id>', methods=['GET'])
@app.route('/profile/files/<id>', methods=['GET'])
def get_files(id):
    if not current_user.is_authenticated:
        return redirect('/login')
    db_sess = db_session.create_session()
    if 'none' not in id.lower():
        ans = db_sess.query(File).filter(File.advrt_id == int(id))
    else:
        return "<h1>Прикреплённых файлов нет.</h1>"
    return render_template('filesGetT.html', title='Файлы', files=ans, user=current_user)


# скачивание файла
@app.route('/file/<id>', methods=['GET'])
def get_file(id):
    db_sess = db_session.create_session()
    name = db_sess.query(File.name).filter(File.id == int(id[0]))[0][0]
    return open(f'notsystemfiles/{current_user.id}/{name}', mode='br').read()


# скачивание/открытие программных файлов
@app.route('/program_file/<name>', methods=['GET'])
def get_program_file(name):
    return open(f'notsystemfiles/admin/{name}', mode='br').read()


@app.route('/pre-chat/<id>/<name>', methods=['GET'])
def start_chat(id, name):
    open(f'notsystemfiles/{current_user.id}/chating/{id} {name}', mode='w', encoding="utf8")
    open(f'notsystemfiles/{id}/chating/{current_user.id} {current_user.name}', mode='w', encoding="utf8")
    return redirect(f'/chat/{id}/{name}')


# demo-chat
@app.route('/chat', methods=['GET', 'POST'])
@app.route('/chat/<id>/<name>', methods=['GET', 'POST'])
def chat(id='', name='', text=''):
    if not current_user.is_authenticated:
        return redirect('/login')
    if "search_text" in request.form and request.form["search_text"].strip():
        return redirect(f'/search/{request.form["search_text"]}')
    if request.method == 'GET' and id:
        return render_template('demo_chat_personT.html',
                               obj=
                               open(f"notsystemfiles/{current_user.id}/chating/{id} {name}", mode='r',
                                    encoding="utf8").read().split(
                                   ':{$~<e0mb4~?n0s.d~>@#['),
                               obj_name=name,
                               obj_i=f"{id} {name}",
                               user=current_user)
    if request.method == 'GET':
        # список "айди - переписка".
        lst = [i.split() for i in os.listdir(f'notsystemfiles/{current_user.id}/chating')]
        return render_template('demo_chatT.html', obj=lst, user=current_user)
    if request.method == 'POST':
        f_last = ''
        if os.path.isfile(f'notsystemfiles/{current_user.id}/chating/{id} {name}'):
            f_last = open(f'notsystemfiles/{current_user.id}/chating/{id} {name}', mode='r',
                          encoding="utf8").read()
        f = open(f"notsystemfiles/{current_user.id}/chating/{id} {name}", mode='w',
                 encoding="utf8")
        _res = f_last + '\n' + current_user.name + ':' + request.form["message"].strip() + ':{$~<e0mb4~?n0s.d~>@#['
        f.write(_res)
        f.close()
        f = open(f"notsystemfiles/{id}/chating/{current_user.id} {current_user.name}", mode='w',
                 encoding="utf8")
        f.write(_res)
        f.close()
        return render_template('demo_chat_personT.html',
                               obj=
                               open(f"notsystemfiles/{current_user.id}/chating/{id} {name}", mode='r',
                                    encoding="utf8").read().split(
                                   ':{$~<e0mb4~?n0s.d~>@#['),
                               obj_name=name,
                               obj_id=f"{id}",
                               user=current_user)


# скачивание иконки
@app.route('/icon/<id>', methods=['GET'])
def get_icon_file(id):
    try:
        return open(f'notsystemfiles/{int(id)}/icon/icon.bmp', mode='br').read()
    except Exception:
        return '<br><h1>Не удалось открыть иконку, попробуйте обратится в техподдержку.</h1>'


# закачивание иконки профиля
@app.route('/photo_profile/<id_person>', methods=['GET', "POST"])
def get_photo(id_person):
    if not current_user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('fileSelectT.html', title='Загрузка фото профиля', user=current_user)
    if current_user.id == int(id_person):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
        name = request.files['file'].filename
        if '.' in name and name.split('.')[1].lower() in ALLOWED_EXTENSIONS:
            request.files['file'].save(os.path.join(f'notsystemfiles/{current_user.id}/icon', 'icon.bmp'))
            if ((os.path.getsize(f'notsystemfiles/{current_user.id}/icon/icon.bmp') / 1024) / 1024) < 1:
                print("success saver")
                return redirect('/profile')
    return False


# настройки
@app.route('/configuration', methods=['GET'])
def configuration():
    if not current_user.is_authenticated:
        return redirect('/login')
    db_sess = db_session.create_session()
    bolean = db_sess.query(Config).filter(Config.person_id == current_user.id)[0].search
    return render_template('configurationT.html', title='Настройки', user=current_user, bolean=bolean)


# открытие профиля
@app.route('/profile', methods=['GET'])
def profile():
    if not current_user.is_authenticated:
        return redirect('/login')
    return render_template('profileT.html', title='Поиск', user=current_user)


# открытие профиля, публичная версия
@app.route('/profile/vp/<id>', methods=['GET'])
def profilePub(id):
    db_sess = db_session.create_session()
    this_user = db_sess.query(User).filter(User.id == int(id))[0]
    _icon_bool = 1 if os.path.isdir(f'notsystemfiles/{current_user.id}/icon') else 0
    return render_template('profilePubT.html', title=this_user.name, user=this_user, _icon=_icon_bool)


# открытие объявлений
@app.route('/profile/adverts', methods=['GET', "POST"])
def adverts():
    if not current_user.is_authenticated:
        return redirect('/login')
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


# закачивание файла на сервер
@app.route('/profile/adverts/files/download/<id_advrt>/<id_person>', methods=['GET', "POST"])
def selecting_files_in_advert(id_advrt, id_person):
    if not current_user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('fileSelectT.html', title='Загрузка файлов', user=current_user)
    if current_user.id == int(id_person):
        db_sess = db_session.create_session()
        advert = db_sess.query(Advert).filter(Advert.id == id_advrt).first()
        buff = saver(request.files['file'], advert.img_id)
        if not buff:
            return "<h1>Неверный формат имени файла.</h1>"

        filename = secure_filename(request.files['file'].filename)
        if len(filename):
            file = File(advrt_id=id_advrt, name=filename)
            db_sess.add(file)
            if buff and buff != 'continue':
                advert.img_id = db_sess.query(File).filter(File.advrt_id == id_advrt,
                                                           File.name == filename).first().id
            db_sess.commit()
    return redirect(f'/profile/adverts')


# сохранение файла
def saver(file, advert_img):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'bmp'}
    IMG_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
    filename = file.filename
    if '.' in filename and filename.split('.')[1].lower() in ALLOWED_EXTENSIONS:
        if not os.path.isdir(f'notsystemfiles/{current_user.id}'):
            os.mkdir(f"notsystemfiles/{current_user.id}")
        # безопасно извлекаем имя файла
        name = secure_filename(file.filename)
        print(name.split('.'))
        if len(name) and '.' in name and len(name.split('.')[0]):
            file.save(os.path.join(f'notsystemfiles/{current_user.id}', name))
            if ((sum([os.path.getsize(f'notsystemfiles/{current_user.id}/{i}') for i in
                      os.listdir(f'notsystemfiles/{current_user.id}')]) / 1024) / 1024) < 1025:
                print("success saver")
                if advert_img == -1 and filename.split('.')[1].lower() in IMG_EXTENSIONS:
                    return True
                return 'continue'
    poper(name)
    return False


def poper(filename):
    if os.path.isfile(os.path.join(f'notsystemfiles/{current_user.id}', filename)):
        os.remove(os.path.join(f'notsystemfiles/{current_user.id}', filename))
        print("success poper")


# создать новое объявление
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
        files = db_sess.query(File).filter(File.advrt_id == id)
        for file in files:
            try:
                os.remove(f'notsystemfiles/{current_user.id}/{file.name}')
            except FileNotFoundError:
                pass
            db_sess.delete(file)
        db_sess.delete(del_advert)
        db_sess.commit()
        return redirect('/profile/adverts')
    return render_template('deletion_confirmation.html', text=f"объявление \"{del_advert.name}\"", user=current_user)


@app.route('/help', methods=['GET'])
def help():
    return render_template('helpT.html', title='Помощь', user=current_user)


@app.route('/about_developers', methods=['GET'])
def about_developers():
    return render_template('about_developersT.html', title='О разработчиках', user=current_user)


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
        id = db_sess.query(User).filter(User.address == form.address.data).first().id
        # создание нужных файлов и директорий
        os.mkdir(f'notsystemfiles/{id}')
        os.mkdir(f"notsystemfiles/{id}/icon")
        _icon = open('notsystemfiles/admin/icon.bmp', mode='br').read()
        with open(f'notsystemfiles/{id}/icon/icon.bmp', mode='wb') as f:
            f.write(_icon)
        os.mkdir(f'notsystemfiles/{id}/chating')
        return redirect('/login')
    return render_template('registerT.html', title='Регистрация', form=form, user=current_user)


# удаление пользователя
@app.route('/profile/delete_profile', methods=['GET', 'POST'])
def delete_profile():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        adverts = db_sess.query(Advert).filter(Advert.id_person == current_user.id)
        configs = db_sess.query(Config).filter(Config.person_id == current_user.id).first()
        db_sess.delete(configs)
        for advert in adverts:
            files = db_sess.query(File).filter(File.advrt_id == advert.id)
            [db_sess.delete(file) for file in files]
            db_sess.delete(advert)
        try:
            shutil.rmtree(f'notsystemfiles/{current_user.id}')
        except FileNotFoundError:
            pass
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
