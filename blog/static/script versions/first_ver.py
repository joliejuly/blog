import datetime
#blog_date = str(datetime.datetime.now())

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
    return render_template('index.html')
    
@app.route('/create', methods = ["GET", "POST"])
def create():
    if request.method == "POST":
        if request.form["title"] and request.form["content"]:
            
            title = request.form.get("title")
            content = request.form.get("content")
            
            #myData = []
            mytuple = (title, content)
            #myData.append(mytuple)

            
            conn = sqlite3.connect("myblog.db")
            db = conn.cursor()
            db.execute("""insert into entries(title, content)
                               values(?, ?)""", mytuple)
            conn.commit()
            conn.close()
            flash("You have created your post successfully")
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
 
