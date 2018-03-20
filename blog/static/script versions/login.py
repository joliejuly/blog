#!usr/bin/python

import functools
import time
import sqlite3

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
            else:
                mytuple = (title, content, 0, localtime)
                db.execute("""insert into entries(title, content, published, date) values(?, ?, ?, ?)""", mytuple)
                
            flash("Your post has been created successfully")
            conn.commit()
            conn.close()
                    
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
 
