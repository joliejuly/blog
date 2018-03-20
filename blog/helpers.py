#!usr/bin/python
# -*- coding: utf-8 -*-
import re
import sqlite3

from flask_mail import Mail, Message
from threading import Thread
from blog import app, mail

from unidecode import unidecode

from flask import g, render_template

def slugify(title):
    
    """ Makes a url-valid string 
        from blog title including 
        non-Latin words. Cyrillic supported. """
        
    # "ванна" – "vanna"
    url = unidecode(title).lower()
    # delete ' instead of "Ь"
    url = re.sub(r"\'", "", url)
    # replace !:,":,": with spaces
    url = re.sub(r"\W+", " ", url)
    # replace spaces with "how-to-use-rubber-duck"
    url = re.sub(r"\s", "-", url)
    # delete trailing signs (how- how)
    url = re.sub(r"\W$", "", url)
    # delete symbols at the beginning of the string (-how how)
    url = re.sub(r"^\W", "", url)
    return url
    
def get_db():
    if not hasattr(g, 'sqlite_db'):
        conn = sqlite3.connect("myblog.db")
        conn.row_factory = sqlite3.Row
        g.sqlite_db = conn
    return g.sqlite_db

def g_top_5():
    if not hasattr(g, 'entries_top_5'):
        conn = sqlite3.connect("myblog.db")
        conn.row_factory = sqlite3.Row
        db = conn.cursor()
        
        # посты для топ 5
        mytuple = (1, 1)
        db.execute("""select title, url from fts_entries 
               where top5 = ? and published = ?""", 
               mytuple)
        g.entries_top_5 = db.fetchall()
    return g.entries_top_5 


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = render_template("follower_email.txt")
    msg.html = render_template("follower_email.html")
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
