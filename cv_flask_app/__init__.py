import os
import json
from flask import Flask, render_template, abort, send_file, request, session, redirect, url_for
from werkzeug.utils import secure_filename
from random import shuffle
from change_mode import get_time
from users import users


app = Flask(__name__)

app.secret_key = os.urandom(12).hex()

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    if 'loged_in' in session and session['loged_in']:
        return render_template('index.html', **users[session['id']], style_mode=get_time())
    return render_template('/auth/login.html', style_mode=get_time())

@app.route('/<user>')
def test(user:str):
    for i in range(len(users)):
        if user.capitalize() in users[i]['full_name'].split(' ')[0]:
            return render_template('index.html', **users[i], style_mode=get_time())
    return abort(404)

@app.route('/register', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        user = dict()

        email = request.form.get('u_mail')
        for i in range(len(users)):
            if email == users[i]['mail']:
                return render_template('/auth/register.html', style_mode=get_time(), msg='User with this email already exists.')
        user['mail'] = email

        passw = request.form.get('u_pass')
        user['password'] = passw

        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        fthr_name = request.form.get('fthr_name')
        if fthr_name:
            user['full_name'] = ' '.join((l_name, f_name, fthr_name))
        else:
            user['full_name'] = ' '.join((l_name, f_name))

        b_day = request.form.get('b_day')
        _temp = b_day.split('-')
        _temp.reverse()
        user['birthdate'] = '/'.join(_temp)

        LIn = request.form.get('linked_in')
        if LIn:
            user['LinkedIn'] = LIn

        tel = request.form.get('u_tel')
        user['tel'] = tel

        edu = request.form.get('u_edu')
        user['education'] = edu

        skills = request.form.get('u_skill')
        user['skills'] = skills

        exp = request.form.get('u_exp')
        user['experience'] = exp

        img_file = request.files['u_img']
        if img_file.filename == '':
            session['loged_in'] = True
            session['id'] = len(users)
            session['email'] = email
            users.append(user)
            return redirect('/')
        
        if not allowed_file(img_file.filename):
            return render_template('/auth/register.html', msg='Invalid image format!', style_mode=get_time())

        if img_file:
            img_filename = secure_filename(img_file.filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))

            user['u_img'] = img_filename
            session['loged_in'] = True
            session['id'] = len(users)
            session['email'] = email
            users.append(user)
            return redirect('/')
        
    return render_template('/auth/register.html', style_mode=get_time())

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('u_mail')
        passw = request.form.get('u_pass')
        for i in range(len(users)):
            if email == users[i]['mail']:
                if passw == users[i]['password']:
                    session['loged_in'] = True
                    session['id'] = i
                    session['email'] = email
                    return redirect('/')
                else:
                    return render_template('/auth/login.html', style_mode=get_time(), msg='Incorrect password!')
    return render_template('/auth/login.html', style_mode=get_time())

@app.errorhandler(404)
def error_404(code):
    return send_file('static/error_404.html')

@app.route('/api')
def api():
    if 'count' in request.args.keys():

        if int(request.args['count']) > len(users):
            return json.dumps(users)
        if int(request.args['count']) <= 0:
            return json.dumps([])
        
        res_obj = users.copy()
        shuffle(res_obj)
        res_obj = res_obj[:int(request.args['count'])]
        return json.dumps(res_obj)
    
    if 'email' in request.args.keys():
        for i in range(len(users)):
            # mail is better cause its unique (and no spaces)
            if request.args['email'] in users[i]['mail']:
                return json.dumps(users[i])
        return json.dumps([])

    if 'name' in request.args.keys():
        for i in range(len(users)):
            if request.args['name'].capitalize() in users[i]['full_name']:
                return json.dumps(users[i])
        return json.dumps([])
    
    return json.dumps(users)

app.run(debug=True)