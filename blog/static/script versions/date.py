#!usr/bin/python

#DOESN"T WORK AS EXPECTED VIA ONE-PROCESS_AT_A_TIME_BACKEND_THING

#нужен параллельный процесс (ajax или сервер) который будет проверять публикации  

import datetime
import functools
import time
import sqlite3
import re

from flask import (Flask, request, render_template, session, url_for, 
                   redirect, flash)

app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.password = 'grower?dower!'
#app.database = 'myblog.db'
#app.config['DEBUG'] = True

#login required wrapper
def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get("logged_in"):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner 

def publish_later(desired_time, rowid):
    
    """ Checks if it is time 
               to publish an entry """
               
    while(1):
        time_now = datetime.datetime.now()
        time_now = time_now.timestamp()
        post_time = datetime.datetime.strptime(desired_time, "%Y-%m-%d-%H-%M")
        post_time = post_time.timestamp()
        
        if time_now >= post_time:
            break
            
    conn = sqlite3.connect("myblog.db")
    db = conn.cursor()
    mytuple = (1, rowid)
    db.execute("update entries set published=? where rowid=?", mytuple)

@app.route('/')
def index():
    conn = sqlite3.connect("myblog.db")
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    mytuple = (1,)
    db.execute("select * from entries where published=? order by rowid desc", mytuple)
    entries = db.fetchall()
    # 
    return render_template('index.html', entries=entries)

@app.route('/create', methods = ["GET", "POST"])
@login_required   
def create():
    if request.method == "POST":
        if request.form["title"] and request.form["content"]:
            
            conn = sqlite3.connect("myblog.db")
            db = conn.cursor()
            
            title = request.form.get("title")
            content = request.form.get("content")
            localtime = time.asctime( time.localtime(time.time()) )

            if request.form.get("published"):
                mytuple = (title, content, 1, localtime)
                db.execute("""insert into entries(title, content, published, date) values(?, ?, ?, ?)""", mytuple)
                conn.commit()
                conn.close()
            else:
                mytuple = (title, content, 0, localtime)
                db.execute("""insert into entries(title, content, published, date) values(?, ?, ?, ?)""", mytuple)
                conn.commit()
                
                if request.form.get("to_be_published"):
                    
                    #datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
                    #outputs 2017-10-11-15-26 (2017, 11 oct, 15:26)
                    
                    # this will be string "2017-10-11T09:00"
                    to_be_published = request.form.get("to_be_published")
                    
                    #makes from 2017-10-11T09:00 this: 2017-10-11-09-00
                    to_be_published = re.sub(r'[T:]', r'-', to_be_published)
                    
                    title = request.form.get("title")
                    mytuple = (title, )
                    
                    db.execute("""select rowid from entries 
                               where title=?
                               """, mytuple)
                    rowid = db.fetchone() #returns a tuple (1, ); to access 1 as int do this: rowid[0]
                    conn.close()
                    flash("Your post has been created successfully")
                    publish_later(to_be_published, rowid[0])
                    
            conn.close()    
            flash("Your post has been created successfully")
            
                    
        else:
            flash("You haven't entered text or title")
            return render_template('create.html')
    return render_template('create.html')
    
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == app.password:
            session['logged_in'] = True
            flash("You are logged in")
            return redirect(url_for("index"))
        else:
            flash("Sorry, wrong password")
            return render_template('login.html')
    return render_template("login.html")

  
@app.route('/edit', methods=["POST", "GET"])
@login_required   
def edit():
    conn = sqlite3.connect("myblog.db")
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    
    if request.method == "POST":
        
        if request.form.get("edit_btn") == "edit":
            entry_id = int(request.form.get("edit"))
            mytuple = (entry_id, )
            db.execute("select rowid, * from entries where rowid=?", mytuple)
            entry = db.fetchone()
            return render_template("edit1.html", entry=entry)
        
        if request.form.get("delete") == "delete":
            entry_id = int(request.form.get("edit"))
            mytuple = (entry_id, )
            db.execute("delete from entries where rowid=?", mytuple)
            conn.commit()
            flash("Entry has been deleted successfully")
            return redirect(url_for("edit"))
        
    else:
        mytuple = (1,)
        db.execute("select rowid, * from entries where published=? order by rowid desc", mytuple)
        entries = db.fetchall()  
        conn.close()
        return render_template('edit.html', entries=entries)

     
@app.route("/update", methods=["POST", "GET"])
@login_required   
def update():
    if request.method == "POST":
        conn = sqlite3.connect("myblog.db")
        conn.row_factory = sqlite3.Row
        db = conn.cursor()
        
        rowid = int(request.form.get("rowid"))
        title = request.form.get("title")
        content = request.form.get("content")
        mydic = {"title": title, 
                 "content": content,
                 "rowid": rowid}
        
        db.execute("""update entries set 
                       title=:title, 
                       content=:content
                       where rowid=:rowid""", mydic)
        conn.commit()
        conn.close()
        flash("Changes saved successfully")
            
        return redirect(url_for("edit"))
    return redirect(url_for("edit"))


@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    if request.method == "POST":
        session.clear()
        flash('You are logged out')
        return redirect(url_for('index'))
    return redirect(url_for('login'))


if __name__ == '__main__':
  app.run(debug=True)
 
