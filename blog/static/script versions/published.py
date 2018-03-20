import datetime
#blog_date = str(datetime.datetime.now())
#localtime = time.asctime( time.localtime(time.time()) )

import sqlite3

from flask import (Flask, request, render_template, session, url_for, 
                   redirect, flash)

app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.password = 'grower?dower!'
app.database = 'myblog.db'
app.config['DEBUG'] = True

@app.route('/')
def index():
    conn = sqlite3.connect("myblog.db")
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    mytuple = (1,)
    db.execute("select * from entries where published=?", mytuple)
    entries = db.fetchall()
    # 
    return render_template('index.html', entries=entries)
    
@app.route('/create', methods = ["GET", "POST"])
def create():
    if request.method == "POST":
        if request.form["title"] and request.form["content"]:
            
            conn = sqlite3.connect("myblog.db")
            db = conn.cursor()
            
            title = request.form.get("title")
            content = request.form.get("content")
            
            if request.form.get("published"):
                mytuple = (title, content, 1)
                db.execute("""insert into entries(title, content, published)
                               values(?, ?, ?)""", mytuple)
            else:
                mytuple = (title, content, 0)
                db.execute("""insert into entries(title, content, published)
                               values(?, ?, ?)""", mytuple)
                
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
    
@app.route('/edit')
def edit():
    return render_template('edit.html')
    
@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You are logged out')
    return redirect(url_for('index'))


if __name__ == '__main__':
  app.run(debug=True)
 
