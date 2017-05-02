#coding=utf-8 

# all the imports
import os
import sqlite3
import math
from datetime import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, PasswordField, RadioField, SubmitField, FileField, HiddenField
from wtforms.validators import DataRequired, ValidationError
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from MD5 import md5

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

    def validate_time_span(form, field):
        if field.data is None or 'None' == field.data:
            raise ValidationError(u'请选择投资时间')

class ExtractFromStaticPurseForm(FlaskForm):
    purse_type = RadioField(u'选择钱包', choices=[('static_purse', u'静态钱包'), ('dynamic_purse', u'动态钱包')], validators=[DataRequired(message=u'请选择钱包')])
    #charge = TextField(u'排单币', validators=[DataRequired(message=u'请填写排单币')])
    amount = TextField(u'按说明输入金额', validators=[DataRequired(message=u'请填写金额')])
    submit = SubmitField(u'提交')

    def validate_amount(form, field):
        amount_int = None
        try:
            amount_int = int(field.data)
        except Exception, e:
            raise ValidationError(u'请输入合法数字')
        if amount_int < 100 or 0 != amount_int % 100:
            raise ValidationError(u'请输入大于等于100的100的倍数')

    def validate_purse_type(form, field):
        if field.data is None or 'None' == field.data:
            raise ValidationError(u'请选择钱包')

class UploadCertificateForm(FlaskForm):
    #entry_id = HiddenField(u"Field1")
    feedback = RadioField(u'请选择', choices=[('yes', u'已打款'), ('no', u'拒绝打款')], validators=[DataRequired(message=u'请选择')])
    certificate = FileField(u'上传文件', validators=[DataRequired(message=u'请选择文件')])
    submit = SubmitField(u'提交')

    #def set_entry_id(self, entry_id):
    #    self.entry_id.data = entry_id

class ConfirmationForm(FlaskForm):
    feedback = RadioField(u'请选择', choices=[('confirm', u'确认收款'), ('fraud', u'未收到款投诉')], validators=[DataRequired(message=u'请选择')])
    
    graph = FileField(u'上传截图', validators=[])
    submit = SubmitField(u'提交')

    def validate_feedback(form, field):
        if field.data is None or 'None' == field.data:
            raise ValidationError(u'请选择')


class SendPaiOrJhmaForm(FlaskForm):
    UE_phone = TextField(u'电话号码', validators=[DataRequired(message=u'请填写电话号码')])
    object_type = RadioField(u'发送对象', choices=[('pai', u'排单币'), ('jhma', u'激活码')], validators=[DataRequired(message=u'')])
    amount = TextField(u'发送数量', validators=[DataRequired(message=u'请填写发送数量')])
    submit = SubmitField(u'提交')

    def validate_amount(form, field):
        amount_int = None
        try:
            amount_int = int(field.data)
        except Exception, e:
            raise ValidationError(u'请输入合法数字')
        if amount_int <= 0:
            raise ValidationError(u'请输入正整数')

    def validate_object_type(form, field):
        if field.data is None or 'None' == field.data:
            raise ValidationError(u'请选择发送对象')


class DynamicPurseForm(FlaskForm):
    amount = TextField(u'转化金额', validators=[DataRequired(message=u'请填写转化金额')])
    submit = SubmitField(u'提交')

    def validate_amount(form, field):
        amount_int = None
        try:
            amount_int = int(field.data)
        except Exception, e:
            raise ValidationError(u'请输入合法数字')
        if amount_int <= 0 or 0 != amount_int % 200:
            raise ValidationError(u'请输入大于0、200的倍数')


class AccountSettingForm(FlaskForm):
    weixin = TextField(u'微信号', validators=[])
    zfb = TextField(u'支付宝帐号', validators=[])
    yhmc = TextField(u'银行卡号', validators=[])
    
    submit = SubmitField(u'提交', id='submit')


class myForm(FlaskForm):
    fileName = FileField(u'my_file', validators=[DataRequired(message=u'请选择文件')])
