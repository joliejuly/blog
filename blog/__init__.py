#!usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3
import time

from flask import (Flask, request, render_template, session, url_for, 
                   redirect, g, flash, abort)

from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yXR~XHH!jmN]LWX/,?RT'
app.password = 'grower?dower!'
app.database = 'myblog.db'
app.config['DEBUG'] = True

csrf = CSRFProtect(app)

# email configurations

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "joliejuly@gmail.com"
app.config['MAIL_PASSWORD'] = "msgauczimgndvxwk"

mail = Mail(app)

class EmailForm(FlaskForm):
    email = StringField("email", validators=[ DataRequired(), Email() ])

import blog.views

