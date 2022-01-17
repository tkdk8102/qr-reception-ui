from flask import Flask, flash, render_template, request, redirect, url_for, session, abort, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
import shutil
import os
import secrets
import datetime
import tempfile
import csv
import uuid
import qrcode
from chardet import detect
from library import db_manager
from library import db_config

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config["JSON_AS_ASCII"] = False
csrf = CSRFProtect(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{user}:{passwd}@{host}:{port}/{db}?charset={charset}'.format(**db_config.users_db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['BCRYPT_HANDLE_LONG_PASSWORDS'] = True
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'hosts'
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(60))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    # QRコード置き場がなければ作る
    os.makedirs('./protected', exist_ok=True)
    # リクエストのたびにセッションの寿命を更新する
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(hours=12)
    session.modified = True

@app.after_request
def after_request(response):
    # クリックジャッキング対策
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

@app.route('/qr/<path:filename>')
@login_required
def qr(filename):
    return send_from_directory('protected', filename)

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":

        account  = request.form['account']  # 入力されたアカウント
        password = request.form['password'] # 入力されたパスワード

        user = User.query.filter_by(account=account).first() # DBユーザ検索
        if user:
            if bcrypt.check_password_hash(user.password, password + account):
                login_user(user)
                if 'next' in request.args:
                    return redirect(request.args['next'])
                else:
                    return redirect(url_for('index'))
        flash('Your account or password cannot be recognized.')
        return render_template("login.html")

    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/reader', methods=['GET'])
@login_required
def reader():
    return render_template('reader.html')

@app.route('/result', methods=['POST'])
@login_required
def result(gid=None):
    guests = db_manager.Connector()
    guests.connect(**db_config.users_db, table='guests')
    res = guests.update_attend(str(request.form['gid']))
    guests.close()
    return jsonify({'kanji_name': res})

@app.route('/guests', methods=['GET'])
@login_required
def guests():
    guests = db_manager.Connector()
    guests.connect(**db_config.users_db, table='guests')
    data = guests.get_guest()
    guests.close()

    return render_template('guests.html', guests=data)

@app.route('/edit', methods=['POST'])
@login_required
def edit():
    guests = db_manager.Connector()
    guests.connect(**db_config.users_db, table='guests')
    guests.edit_guest(
        guest_id   = request.form['id'],
        attendance = request.form['attendance'],
        kanji_name = request.form['kanji_name'],
        kana_name  = request.form['kana_name'],
        relation   = request.form['relation'],
        reward     = request.form['reward'],
        note       = request.form['note']
    )
    guests.close()
    return redirect(url_for('guests'))

@app.route('/add', methods=['POST'])
@login_required
def add():
    guests = db_manager.Connector()
    guests.connect(**db_config.users_db, table='guests')
    gid = uuid.uuid4().hex
    last_id = guests.add_guest(
        gid        = gid,
        kanji_name = request.form['kanji_name'],
        kana_name  = request.form['kana_name'],
        relation   = request.form['relation'],
        reward     = request.form['reward'],
        note       = request.form['note']
    )
    guests.close()
    # qrコード生成
    qr = qrcode.QRCode()
    qr.add_data(gid)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save('protected/' + str(last_id) + '.png')

    return redirect(url_for('guests'))

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    guests = db_manager.Connector()
    guests.connect(**db_config.users_db, table='guests')
    guests.del_guest(
        guest_id   = request.form['id']
    )
    guests.close()
    try: # QRコード画像削除
        os.remove('protected/' + request.form['id'] + '.png')
    except:
        pass
    return redirect(url_for('guests'))

@app.route('/download', methods=['GET'])
@login_required
def download():
    with tempfile.TemporaryDirectory() as temp_dir:
        out_dir = temp_dir + '/out'
        os.makedirs(out_dir)
        qrs = os.listdir('protected')
        # 招待者名の取得
        guests = db_manager.Connector()
        guests.connect(**db_config.users_db, table='guests')
        for qr in qrs:
            guest_id, png = os.path.splitext(qr)
            kanji = guests.get_name(
                guest_id = guest_id
            )
            # ファイル名を 招待者様_ID.png に変更して ZIP
            filename = kanji.replace(' ', '_') + '様_' + str(guest_id) + png
            shutil.copy('protected/' + qr, out_dir + '/' + filename)
        guests.close()
        shutil.make_archive(temp_dir + '/qr_codes', 'zip', root_dir=out_dir)
        return send_from_directory(temp_dir, 'qr_codes.zip', as_attachment=True,
                    attachment_filename='qr_codes_'+str(uuid.uuid4())[-6:]+'.zip')

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    csv_file = request.files['csv_file']
    if csv_file.filename.endswith('.csv'):
        # 一時保存と読み込み
        with tempfile.NamedTemporaryFile() as tempfile_path:
            csv_file.save(tempfile_path.name)
            with open(tempfile_path.name, 'rb') as f:
                enc = detect(f.read())
                f = open(tempfile_path.name, encoding=enc['encoding'], errors='replace')
                reader = csv.reader(f)
        # DB書き込み
        for r, row in enumerate(reader):
            guests = db_manager.Connector()
            guests.connect(**db_config.users_db, table='guests')
            if r == 0:
                for c, label in enumerate(row):
                    if '出欠' == label:
                        atnd = c
                    if '姓' == label:
                        kanji_sei = c
                    if '名' == label:
                        kanji_mei = c
                    if '姓（ふりがな）' == label:
                        kana_sei = c
                    if '名（ふりがな）' == label:
                        kana_mei = c
            elif 'ご出席' == row[atnd]:
                gid = uuid.uuid4().hex
                last_id = guests.add_guest(
                    gid        = gid,
                    kanji_name = row[kanji_sei] + ' ' + row[kanji_mei],
                    kana_name  = row[kana_sei] + ' ' + row[kana_mei]
                )
                # qrコード生成
                qr = qrcode.QRCode()
                qr.add_data(gid)
                img = qr.make_image(fill_color="black", back_color="white")
                img.save('protected/' + str(last_id) + '.png')
            guests.close()
    else:
        abort('Not allowed file.')

    return redirect(url_for('guests'))
