import os
import json
from random import shuffle
from datetime import datetime
from flask import render_template, abort, send_file, request, session, redirect
from werkzeug.utils import secure_filename
from users import users
from models import *


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename) -> bool:
    '''
    Функция проверки расширения файла (для картинок).
    Возвращает True если расширение картинки подходит, в обратном случае - False.
    '''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_time() -> str:
    """
    Функция для определения текущего времени пользователя (для смены темы сайта).
    """
    t = datetime.now().hour
    if 6 < t < 18:
        return 'light'
    else:
        return 'dark'


def fill_db() -> None:
    # чтобы заполнить базу искуственными данными (для проверки работоспособности).
    with app.app_context():
        exist_users = db.session.query(Users).all()
        if exist_users:
            return

        for record in users:
            users_obj = Users(**record)
            db.session.add(users_obj)

        db.session.commit()


@app.route('/')
def main():
    # Функция для главной страницы.
    # Возвращает страницу пользователя, если он уже зарегестрирован и вошел в систему.
    # В другом случае возвращает страницу входа.

    if 'loged_in' in session and session['loged_in']:
        user = db.session.query(Users).filter(Users.id == session['id']).first()
        return render_template('index.html', data=user, style_mode=get_time())
    return render_template('auth/login.html', style_mode=get_time())


@app.route('/users/<l_name>/', defaults={'f_name': None})
@app.route('/users/<l_name>/<f_name>')
def user_ref_last_name(l_name: str, f_name: str):
    if f_name:
        found_user = db.session.query(Users).filter(
            Users.last_name == l_name.capitalize()
        ).filter(
            Users.first_name == f_name.capitalize()
        ).first()
    else:
        found_user = db.session.query(Users).filter(Users.last_name == l_name.capitalize()).first()

    if found_user:
        return render_template('index.html', data=found_user, style_mode=get_time())
    return abort(404)


@app.route('/register', methods=['GET', 'POST'])
def reg():
    # Функция для страницы регистрации.

    if request.method == 'POST':
        user = dict()

        email = request.form.get('u_mail')
        user_exists = db.session.query(Users).filter(Users.mail == email).first()
        if user_exists:
            return render_template(
                    '/auth/register.html', style_mode=get_time(), msg='User with this email already exists.'
                )
        user['mail'] = email

        passw = request.form.get('u_pass')
        user['password'] = passw

        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        fthr_name = request.form.get('fthr_name')
        user['first_name'] = f_name.capitalize()
        user['last_name'] = l_name.capitalize()
        if fthr_name:
            user['fathers_name'] = fthr_name.capitalize()

        b_day = request.form.get('b_day')
        _temp = b_day.split('-')
        _temp.reverse()
        user['birthdate'] = '/'.join(_temp)

        l_in = request.form.get('linked_in')
        if l_in:
            user['LinkedIn'] = l_in

        tel = request.form.get('u_tel')
        user['tel'] = tel

        edu = request.form.get('u_edu')
        user['education'] = edu

        skills = request.form.get('u_skill')
        user['skills'] = skills

        exp = request.form.get('u_exp')
        user['experience'] = exp

        db.session.add(Users(**user))
        cur_user = db.session.query(Users).filter(Users.mail == user['mail']).first()
        db.session.commit()

        img_file = request.files['u_img']
        if img_file.filename == '':
            session['loged_in'] = True
            session['id'] = cur_user.id
            return redirect('/')

        if not allowed_file(img_file.filename):
            return render_template('/auth/register.html', msg='Invalid image format!', style_mode=get_time())

        if img_file:
            img_filename = secure_filename(img_file.filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))

            cur_user.u_img = img_filename
            db.session.commit()
            session['loged_in'] = True
            session['id'] = cur_user.id
            return redirect('/')

    return render_template('/auth/register.html', style_mode=get_time())


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Функция для страницы входа.

    if request.method == 'POST':
        email = request.form.get('u_mail')
        passw = request.form.get('u_pass')
        user = db.session.query(Users).filter(Users.mail == email).first()

        # Проверяет есть ли такой пользователь в базе данных и совпадает ли введенный пароль с паролем в базе.
        if not user:
            return render_template('/auth/login.html', style_mode=get_time(), msg='No such user registered!')

        if user.password != passw:
            return render_template('/auth/login.html', style_mode=get_time(), msg='Incorrect password!')

        # Записывает id пользователя и его статус (вошел в систему) в сессию.
        # После, переадресовывает на главную страницу.
        session['loged_in'] = True
        session['id'] = user.id
        return redirect('/')

    return render_template('/auth/login.html', style_mode=get_time())


@app.errorhandler(404)
def error_404(code):
    return send_file('static/error_404.html')


@app.route('/api')
def api():
    # Функция для создания/отображения API со списком пользователей. По дефолту выводит всех пользователей.

    # lambda функция создает словарь из объекта класса. С ее помощью создается список словарей всех пользователей.
    row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
    all_users_obj = db.session.query(Users).all()
    all_users = []
    res_api = []
    for el in all_users_obj:
        all_users.append(row2dict(el))

    count = 'count' in request.args.keys()
    last_name = 'last_name' in request.args.keys()

    # Если есть параметр last_name - выводит список из всех пользователей с такой фамилией.
    # Если таких пользователей нет - выводит пустой список.
    if last_name:
        users_by_name = db.session.query(Users).filter(
            Users.last_name == request.args['last_name'].capitalize()
        ).all()

        if users_by_name:
            for el in users_by_name:
                res_api.append(row2dict(el))
            if count:
                return json.dumps(res_api[:int(request.args['count'])])
            return json.dumps(res_api)
        return json.dumps([])

    # Если есть параметр count - выводит список из заданного количества случайных пользователей.
    # Если count больше, чем количество всех пользователей - выводит всех пользователей.
    # Если count 0 или отрицательный - выводит пустой список
    if count:
        if int(request.args['count']) > len(all_users):
            return json.dumps(all_users)
        if int(request.args['count']) <= 0:
            return json.dumps([])

        shuffle(all_users)
        all_users = all_users[:int(request.args['count'])]
        return json.dumps(all_users)

    return json.dumps(all_users)


if __name__ == '__main__':
    fill_db()
    app.run()
