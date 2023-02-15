import os
import json
from __init__ import app, ALLOWED_EXTENSIONS
from flask import render_template, abort, send_file, request, session, redirect, url_for
from werkzeug.utils import secure_filename
from random import shuffle
from change_mode import get_time
from users import users
from models import db, Users


def fill_db():
    # чтобы заполнить базу искуственными данными (для проверки работоспособности)
    with app.app_context():
        db.drop_all()
        db.create_all()
        for record in users:
            users_obj = Users(**record)
            db.session.add(users_obj)
        db.session.commit()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    if 'loged_in' in session and session['loged_in']:
        user = db.session.query(Users).filter(Users.id == session['id']).first()
        return render_template('index.html', data=user, style_mode=get_time())
    return render_template('auth/login.html', style_mode=get_time())


@app.route('/<user>')
def user_ref(user: str):
    found_user = db.session.query(Users).filter(Users.last_name == user.capitalize()).first()
    if found_user:
        return render_template('index.html', data=found_user, style_mode=get_time())
    return abort(404)


@app.route('/register', methods=['GET', 'POST'])
def reg():
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
    if request.method == 'POST':
        email = request.form.get('u_mail')
        passw = request.form.get('u_pass')
        user = db.session.query(Users).filter(Users.mail == email).first()
        if not user:
            return render_template('/auth/login.html', style_mode=get_time(), msg='No such user registered!')

        if user.password != passw:
            return render_template('/auth/login.html', style_mode=get_time(), msg='Incorrect password!')

        session['loged_in'] = True
        session['id'] = user.id
        return redirect('/')

    return render_template('/auth/login.html', style_mode=get_time())


@app.errorhandler(404)
def error_404(code):
    return send_file('static/error_404.html')


@app.route('/api')
def api():
    # create list of dict from Users objects
    row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}

    all_users = db.session.query(Users).all()
    res = []
    for el in all_users:
        res.append(row2dict(el))

    if 'count' in request.args.keys():
        if int(request.args['count']) > len(all_users):
            return json.dumps(res)

        if int(request.args['count']) <= 0:
            return json.dumps([])

        shuffle(res)
        res = res[:int(request.args['count'])]
        return json.dumps(res)

    if 'last_name' in request.args.keys():
        res.clear()
        users_by_name = db.session.query(Users).filter(
            Users.last_name == request.args['last_name'].capitalize()
        ).all()

        for el in users_by_name:
            res.append(row2dict(el))
            return json.dumps(res)

        return json.dumps([])

    return json.dumps(res)


fill_db()
app.run(debug=True)
