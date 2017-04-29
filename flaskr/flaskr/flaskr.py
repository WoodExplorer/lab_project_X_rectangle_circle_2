#coding=utf-8 

# all the imports
import os
import sqlite3
import math
from datetime import datetime
import decimal
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, PasswordField, RadioField, SubmitField, FileField 
from wtforms.validators import DataRequired, ValidationError
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from MD5 import md5
from my_forms import InvestmentForm, myForm, ExtractFromStaticPurseForm, UploadCertificateForm

decimal.getcontext().prec = 2

engine = create_engine('mysql://root:root@localhost/happykimi?charset=gbk', echo=True)#convert_unicode=True, echo=True)#echo=False)
Base = declarative_base(engine)

from sqlalchemy.orm import relationship, backref

class OT_User(Base):
    """"""
    __tablename__ = 'ot_user'
    __table_args__ = {'autoload':True}

class OT_Tgbz(Base):
    """"""
    __tablename__ = 'ot_tgbz'
    __table_args__ = {'autoload':True}

class OT_Jsbz(Base):
    """"""
    __tablename__ = 'ot_jsbz'
    __table_args__ = {'autoload':True}

class OT_Userget(Base):
    """"""
    __tablename__ = 'ot_userget'
    __table_args__ = {'autoload':True}

class OT_Ppdd(Base):
    """"""
    __tablename__ = 'ot_ppdd'
    __table_args__ = {'autoload':True}

###

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    UPLOAD_FOLDER='./upload',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    #rv = sqlite3.connect(app.config['DATABASE'])
    #rv.row_factory = sqlite3.Row

    conn = engine.connect()
    return conn

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    assert(False)
    init_db()
    print('Initialized the database.')

#########################
@app.route('/')
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    UE_account = session.get('logged_in_account')

    Ses = sessionmaker(bind=engine)
    ses = Ses()

    entries_for_15_days = ses.query(OT_Tgbz).filter_by(user=UE_account, zffs1=1, zt=0, qr_zt=0)
    entries_for_30_days = ses.query(OT_Tgbz).filter_by(user=UE_account, zffs2=1, zt=0, qr_zt=0)
    entries_waiting = ses.query(OT_Tgbz).filter_by(user=UE_account, zt=1)
    
    ses.close()
    return render_template('show_entries.html', 
            entries_for_15_days=entries_for_15_days, entries_for_30_days=entries_for_30_days, entries_waiting=entries_waiting,
        )

@app.route('/entry_waiting_detail/<entry_id>')
def entry_waiting_detail(entry_id):
    if not session.get('logged_in'):
        abort(401)
    UE_account = session.get('logged_in_account')

    Ses = sessionmaker(bind=engine)
    ses = Ses()

    #print '*' * 10, 'got it, entry_id:', entry_id
    # 查询ppdd表中p_id 等于当前订单号的记录
    rec_in_ppdd = ses.query(OT_Ppdd).filter_by(p_id=entry_id)
    assert(1 == rec_in_ppdd.count())
    rec_in_ppdd = rec_in_ppdd[0]

    g_user = ses.query(OT_User).filter_by(UE_account=rec_in_ppdd.g_user)[0]
    p_user = ses.query(OT_User).filter_by(UE_account=rec_in_ppdd.p_user)[0]

    ses.close()
    return render_template('entry_waiting_detail.html', g_user=g_user, p_user=p_user,)

@app.route('/entry_waiting_operation/<entry_id>')
def entry_waiting_operation(entry_id, methods=['GET', 'POST']):
    error_str = None
    flag = False
    form = UploadCertificateForm()
    print '*' * 10
    if request.method == 'POST':
        if form.validate_on_submit():
            filename = secure_filename(form.certificate.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print 'file_path:', file_path
            form.fileName.data.save(file_path)
            flag = True
    if flag:
        return redirect(url_for('show_entries'))
    else:
        return render_template('entry_waiting_operation.html', error=error_str, form=form, entry_id=entry_id)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

def flash_and_close_session(error_str, session):
    flash(error_str)
    session.close()

@app.route('/change_password')
def change_password():
    return render_template('change_password.html')

@app.route('/change_password_backend', methods=['POST'])
def change_password_backend():
    if not session.get('logged_in'):
        abort(401)

    UE_password, new_UE_password, new_UE_password_again, = request.form['UE_password'], request.form['new_UE_password'], request.form['new_UE_password_again']

    if new_UE_password != new_UE_password_again:
        flash(u'两次输入的新密码不一致')
        return redirect(url_for('change_password'))

    Ses = sessionmaker(bind=engine)
    ses = Ses()

    UE_account = session.get('logged_in_account')
    ret = ses.query(OT_User).filter_by(UE_account=UE_account)
    if 0 == ret.count():
        flash_and_close_session(u'用户不存在', ses)
        return redirect(url_for('show_entries'))
    if 1 < ret.count():
        flash_and_close_session(u'存在同名用户', ses)
        return redirect(url_for('show_entries'))

    entry = ret[0]
    if md5(UE_password) != entry.UE_password:
        flash_and_close_session(u'密码错误', ses)
        return redirect(url_for('change_password'))
    
    entry.UE_password = md5(new_UE_password)
    
    ses.commit()
    ses.close()

    flash(u'修改密码成功')
    return redirect(url_for('show_entries'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_backend', methods=['POST'])
def register_backend():  
    UE_account, UE_password, UE_password_again, UE_truename, UE_accName, = request.form['UE_account'], request.form['UE_password'], request.form['UE_password_again'], request.form['UE_truename'], request.form['UE_accName']

    if UE_password != UE_password_again:
        flash(u'两次输入的密码不一致')
        return redirect(url_for('register'))

    #
    Session = sessionmaker(bind=engine)
    ses = Session()

    # insert
    entry = OT_User()
    #entry.ue_id = current_ue_id
    #current_ue_id += 1
    
    # populate fields with information supplied by users
    entry.UE_account = UE_account
    entry.UE_password = md5(UE_password)
    entry.UE_truename = UE_truename
    entry.UE_accName = UE_accName
    
    # populate other fields with not-null constraint
    entry.jihuouser = 'None'
    entry.tx_leiji = 0
    entry.UE_verMail = 'None'
    entry.zcr = UE_account
    entry.UE_regTime = datetime.now()
    
    ses.add(entry)
    ses.commit()
    ses.close()

    #db = get_db()
    #db.execute('insert into ot_user (UE_account, UE_password, UE_truename, UE_accName, UE_nowTime) values (?, ?, ?, ?, ?)',
    #             [UE_account, UE_password, UE_truename, UE_accName, datetime.now()])
    #db.commit()
    flash(u'注册成功')
    return redirect(url_for('show_entries'))

def calc_pai(investment):
    return int(math.ceil(investment / 1000))

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            #flash(u"Error in the %s field - %s" % (getattr(form, field).label.text, error))
            flash(u"错误：%s" % (error))

G_INTEREST_RATE_FOR_15_DAYS = 0.12
G_INTEREST_RATE_FOR_30_DAYS = 0.40
G_MONEY_PER_PAI = 50

@app.route('/static_purse', methods=['GET'])
def static_purse():
    if not session.get('logged_in'):
        abort(401)
    UE_account = session.get('logged_in_account')

    Session = sessionmaker(bind=engine)
    ses = Session()

    entries_for_15_days = ses.query(OT_Tgbz).filter_by(user=UE_account, zffs1=1)
    total_sum_for_15_days = sum(map(lambda x: x.jb, entries_for_15_days))
    total_pai_for_15_days = sum([calc_pai(x.jb) for x in entries_for_15_days])
    #print 'total_sum_for_15_days:', total_sum_for_15_days
    total_profit_for_15_days = float(total_sum_for_15_days) + float(total_sum_for_15_days) * G_INTEREST_RATE_FOR_15_DAYS + float(total_pai_for_15_days) * G_MONEY_PER_PAI

    entries_for_30_days = ses.query(OT_Tgbz).filter_by(user=UE_account, zffs2=1)
    total_sum_for_30_days = sum(map(lambda x: x.jb, entries_for_30_days))
    total_pai_for_30_days = sum([calc_pai(x.jb) for x in entries_for_30_days])
    total_profit_for_30_days = float(total_sum_for_30_days) + float(total_sum_for_30_days) * G_INTEREST_RATE_FOR_30_DAYS + float(total_pai_for_30_days) * G_MONEY_PER_PAI

    ses.close()
    return render_template('static_purse.html', 
        total_profit_for_15_days=total_profit_for_15_days, 
        entries_for_15_days=entries_for_15_days,
        total_profit_for_30_days=total_profit_for_30_days, 
        entries_for_30_days=entries_for_30_days,)

@app.route('/investment', methods=['GET', 'POST'])
def investment():
    if not session.get('logged_in'):
        abort(401)
    UE_account = session.get('logged_in_account')

    error_str = None
    flag = False

    form = InvestmentForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            Session = sessionmaker(bind=engine)
            ses = Session()

            cur_user = ses.query(OT_User).filter_by(UE_account=UE_account)[0]
            cur_time = datetime.now() 

            if 1 == cur_user.UE_status:
                error_str = u'当前帐户已被封号'
                ses.close()
                return render_template('show_entries.html', error=error_str, form=form)


            entry = OT_Tgbz()
            #print dir(form)
            #print 'form.check:'
            #print form.check
            print 'request.form.getlist("time_span")'
            print request.form.getlist("time_span")

            # set time_span
            time_span = request.form.getlist("time_span")[0]
            time_span_days = None
            assert('30_days' == time_span or '15_days' == time_span)
            if '30_days' == time_span:
                entry.zffs2 = 1
                time_span_days = 30
            else:
                entry.zffs1 = 1
                time_span_days = 15

            # check for repeated investment in too short a period
            previous_investments = ses.query(OT_Tgbz).filter_by(user=UE_account).order_by(OT_Tgbz.id.desc())
            if 0 == previous_investments.count():
                pass
            else:
                last_investment = previous_investments[0]
                last_investment_datetime = last_investment.date
                if (cur_time - last_investment_datetime ).total_seconds() < time_span_days * 24 * 3600:
                    error_str = u'您在%d天内已经发起一次投资，不能重复投资' % time_span_days
                    ses.close()
                    return render_template('investment.html', error=error_str, form=form)

            #
            investment = int(form.investment.data)
            entry.jb = investment
            entry.user = UE_account
            entry.user_tjr = cur_user.UE_account
            entry.date = cur_time
            entry.user_nc = cur_user.UE_truename

            # check for enough pai
            charge = calc_pai(investment)
            if cur_user.pai < charge:
                error_str = u'排单币不足，当前排单币为：%d' % cur_user.pai
                ses.close()
                return render_template('investment.html', error=error_str, form=form)
            cur_user.pai -= charge

            ses.add(entry)
            ses.commit()
            ses.close()

            flash(u'投资成功')
            return redirect(url_for('show_entries'))

        else:
            #flash(u'请确保您正确填写了表单')
            flash_errors(form)

    if flag:
        return redirect(url_for('show_entries'))
    else:
        return render_template('investment.html', error=error_str, form=form)

@app.route('/test_upload', methods=['GET', 'POST'])
def test_upload():
    if not session.get('logged_in'):
        abort(401)
    UE_account = session.get('logged_in_account')

    error_str = None
    flag = False
    form = myForm()
    if request.method == 'POST':
        print '*' * 10, ' here'
        if form.validate_on_submit():
            filename = secure_filename(form.fileName.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print 'file_path:', file_path
            form.fileName.data.save(file_path)
    if flag:
        return redirect(url_for('show_entries'))
    else:
        return render_template('test_upload.html', error=error_str, form=form)


def calc_level_users(user, max_level, find_next_level):
    next_queue = [user]
    queue = []
    ret = []
    for _ in xrange(0, max_level):
        queue = next_queue
        next_queue = []
        for q in queue:
            next_queue += find_next_level(q)
        ret.append(next_queue[:])
    return ret


@app.route('/dynamic_purse', methods=['GET', 'POST'])
def dynamic_purse():
    assert(False)

    error_str = None
    flag = False
    form = myForm()
    if request.method == 'POST':
        print '*' * 10, ' here'
        if form.validate_on_submit():
            filename = secure_filename(form.fileName.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print 'file_path:', file_path
            form.fileName.data.save(file_path)
    if flag:
        return redirect(url_for('show_entries'))
    else:
        return render_template('dynamic_purse.html', error=error_str, form=form)


@app.route('/receive_help', methods=['GET', 'POST'])
def receive_help():
    if not session.get('logged_in'):
        abort(401)
    UE_account = session.get('logged_in_account')

    error_str = None
    flag = False
    form = ExtractFromStaticPurseForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            Session = sessionmaker(bind=engine)
            ses = Session()

            cur_user = ses.query(OT_User).filter_by(UE_account=UE_account)[0]
            cur_time = datetime.now() 

            # check: 账号未被封
            if 1 == cur_user.UE_status:
                error_str = u'当前帐户已被封号'
                ses.close()
                return render_template('show_entries.html', error=error_str, form=form)

            # check: 输入的金额不得高于静态钱包的总额
            amount = decimal.Decimal(form.amount.data)
            cur_UE_money = decimal.Decimal(cur_user.UE_money)
            if cur_UE_money <= amount:
                error_str = u'输入的金额不得高于静态钱包的总额'
                ses.close()
                return render_template('receive_help.html', error=error_str, form=form)

            # 更新ot_user表中的UE_money字段
            cur_user.UE_money = str(cur_UE_money - amount)

            # 在jsbz表中添加记录
            entry = OT_Jsbz()
            entry.user = cur_user.UE_account
            entry.jb = amount
            entry.user_nc = cur_user.UE_truename
            entry.user_tjr = cur_user.UE_accName
            entry.date = cur_time
            entry.zt = 0
            entry.qr_zt = 0
            entry.qb = 1
            ses.add(entry)

            # 往userget表中添加记录
            entry = OT_Userget()
            entry.UG_account = cur_user.UE_account
            entry.UG_type = 'jb'
            entry.UG_allGet = amount
            entry.UG_money = '-' + str(amount)
            entry.UG_balance = cur_user.UE_money
            entry.UG_dataType = 'jsbz'
            entry.UG_note = u'静态钱包提现'
            entry.UG_getTime = cur_time
            entry.jiang_zt = 0  # database not-null constraint
            ses.add(entry)

            ses.commit()
            ses.close()

            flash(u'操作成功')
            return redirect(url_for('show_entries'))

        else:
            #flash(u'请确保您正确填写了表单')
            flash_errors(form)


    if flag:
        return redirect(url_for('show_entries'))
    else:
        return render_template('receive_help.html', error=error_str, form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    error_str = None
    flag = False
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']

        Session = sessionmaker(bind=engine)
        ses = Session()

        if ses.query(OT_User).filter_by(UE_account=user_name).count() == 0:
            error_str = u'用户名错误'
        elif md5(password) != ses.query(OT_User).filter_by(UE_account=user_name)[0].UE_password:
            error_str = u'密码错误'
        else:
            flag = True
            session['logged_in'] = True
            session['logged_in_account'] = user_name
            flash(u'登陆成功')
        ses.close()

    if flag:
        return redirect(url_for('show_entries'))
    else:
        return render_template('login.html', error=error_str)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('logged_in_account', None)
    flash(u'登出成功')
    return redirect(url_for('show_entries'))

