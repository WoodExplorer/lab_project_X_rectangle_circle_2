#coding=utf-8 

# all the imports
import os
import sqlite3
import math
from datetime import datetime
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
    
    return render_template('show_entries.html', entries=[])

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

class InvestmentForm(FlaskForm):
    time_span = RadioField(u'投资时间', choices=[('15_days', u'15天'), ('30_days', u'30天')], validators=[DataRequired(message=u'请选择投资时间')])
    #charge = TextField(u'排单币', validators=[DataRequired(message=u'请填写排单币')])
    investment = TextField(u'投资金额', validators=[DataRequired(message=u'请填写投资金额')])
    submit = SubmitField(u'提交')

    def validate_investment(form, field):
        investment_int = None
        try:
            investment_int = int(field.data)
        except Exception, e:
            raise ValidationError(u'请输入合法数字')
        if investment_int <= 0 or investment_int > 5000 or 0 != investment_int % 100:
            raise ValidationError(u'请输入(0,5000]之间的100的倍数')

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
                return render_template('investment.html', error=error_str, form=form)


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

class myForm(FlaskForm):
   fileName = FileField(u'my_file', validators=[DataRequired(message=u'请选择文件')])

@app.route('/test_upload', methods=['GET', 'POST'])
def test_upload():
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

