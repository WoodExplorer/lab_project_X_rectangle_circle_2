#coding=utf-8 

# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, PasswordField, RadioField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from MD5 import md5

engine = create_engine('mysql://root:root@localhost/happykimi?charset=gbk', echo=True)#convert_unicode=True, echo=True)#echo=False)
Base = declarative_base(engine)

from sqlalchemy.orm import relationship, backref

class OT_User(Base):
    """"""
    __tablename__ = 'ot_user'
    __table_args__ = {'autoload':True}

###

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
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
    session = Session()

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
    
    session.add(entry)
    session.commit()
    session.close()

    #db = get_db()
    #db.execute('insert into ot_user (UE_account, UE_password, UE_truename, UE_accName, UE_nowTime) values (?, ?, ?, ?, ?)',
    #             [UE_account, UE_password, UE_truename, UE_accName, datetime.now()])
    #db.commit()
    flash(u'注册成功')
    return redirect(url_for('show_entries'))

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            #flash(u"Error in the %s field - %s" % (getattr(form, field).label.text, error))
            flash(u"错误：%s" % (error))

class InvestmentForm(FlaskForm):
    time_span = RadioField(u'投资时间', choices=[('15_days', u'15天'), ('30_days', u'30天')], validators=[DataRequired(message=u'请选择投资时间')])
    charge = TextField(u'排单币', validators=[DataRequired(message=u'请填写排单币')])
    investment = TextField(u'投资金额', validators=[DataRequired(message=u'请填写投资金额')])
    submit = SubmitField(u'提交')

@app.route('/investment', methods=['GET', 'POST'])
def investment():
    error_str = None
    flag = False


    form = InvestmentForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            entry = Entry()
            print 'form.check:'
            print form.check
            print 'request.form.getlist("check")'
            print request.form.getlist("check")
            form.populate_obj(entry)
            db.session.add(entry)
            db.session.commit()
            flash('New entry was successfully posted')


    
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

        else:
            #flash(u'请确保您正确填写了表单')
            flash_errors(form)

    if flag:
        return redirect(url_for('show_entries'))
    else:

        return render_template('investment.html', error=error_str, form=form)


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

