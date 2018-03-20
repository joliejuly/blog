# -*- coding: utf-8 -*-

import re
import sqlite3
import time

from flask import (abort, g, flash, Flask, redirect, request,         
                   render_template, session, url_for)

from flask_mail import Mail, Message
from threading import Thread


from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField
from wtforms.validators import Email, DataRequired

from blog import app, csrf, mail, EmailForm
from blog.helpers import slugify, get_db, g_top_5, send_email

# http://flask.pocoo.org/docs/0.12/patterns/packages/ for documentation
# configure setuptools, then run pip3 install -e. in the terminal
# it'll create a package, that could be installed as a third-party library

@app.route('/')
def index():
    
    db = g.sqlite_db.cursor()
    # all posts
    mytuple = (1, )
    db.execute("""select rowid, * 
               from fts_entries 
               where published=? 
               order by rowid desc""", 
               mytuple)
    entries = db.fetchall()

    # fixed post at the top
    mytuple = (4, 1)
    db.execute("""select rowid, * from fts_entries 
               where rowid = ? and published = ?""", 
               mytuple)
    pinned_entry = db.fetchone()

    return render_template("index.html", 
                           entries = entries, 
                           pinned_entry=pinned_entry,
                           entries_top_5 = g_top_5())

@app.route('/posts')
def allposts():
    
    # a list of posts sorted by date
    db = g.sqlite_db.cursor()
    mytuple = (1, )
    db.execute("select rowid, * from fts_entries where published=? order by rowid desc", mytuple)
    entries = db.fetchall()
    return render_template("allposts.html", 
                           entries = entries,
                           entries_top_5 = g_top_5())

@app.route('/posts/<url>')
def show_post(url):
    
    db = g.sqlite_db.cursor()
    
    
    mytuple = (1, url)
    db.execute("select rowid, * from fts_entries where published=? and url=?", mytuple)
    entry = db.fetchone()
    return render_template("post.html", 
                           entry = entry,
                           entries_top_5 = g_top_5())
    
@app.route("/subscribe", methods=["GET", "POST"])
def subscribe():
    if request.method == "POST":
        form = EmailForm()
        if form.validate_on_submit():
            
            db = g.sqlite_db.cursor()
            
            email = request.form.get("email")
            mytuple = (email, )
            db.execute("insert into subscribers (email) values (?)", mytuple)
            get_db().commit()

            flash("You have subscribed successfully!")
            
            send_email("Hello",
                  sender="joliejuly@gmail.com",
                  recipients=[email])
            
            return redirect(url_for("allposts"))
        else:
            flash("Not valid email")
            return redirect(url_for("allposts"))
        
    return redirect(url_for("allposts"))

@app.route('/top_5', methods = ["GET", "POST"])
def top_5():
    if request.method == "POST":
        db = g.sqlite_db.cursor()
        
        # adding post to TOP-5
        if request.form.get("add_to_top5"):
            # check how many TOP-5 posts already exist
            db.execute(""" select count(*) 
                       from fts_entries
                       where top5 !=0
                       """)
            # fetchone returns a tuple like (1, )
            count = db.fetchone()[0]
            if count < 5:
                rowid = request.form.get("rowid")
                
                mydic = { 
                            "top5": 1,
                            "rowid": rowid
                        }
                db.execute("""update fts_entries set 
                               top5=:top5
                               where rowid=:rowid""", mydic)
                get_db().commit()
                flash("Post has been added to top5 successfully")
                return redirect(url_for("admin_posts"))
            else:
                flash("Too many posts in top5 already. Please, remove some")  
                return redirect(url_for("admin_posts"))
    
        if request.form.get("remove_from_top5"):
            rowid = request.form.get("rowid")
            mydic = { 
                        "top5": 0,
                        "rowid": rowid
                    }
            db.execute("""update fts_entries set 
                           top5=:top5
                           where rowid=:rowid""", mydic)
            get_db().commit()
            flash("Post has been removed from top5 successfully")
            return redirect(url_for("admin_posts"))
        
    return redirect(url_for("admin_posts"))
    
#-----------------------------------------------
# ADMIN (USER-INVISIBLE) ROUTS


@app.route('/admin_posts')
def admin_posts():
    
    db = g.sqlite_db.cursor()

    # fixed post

    mytuple = (4, )
    
    db.execute("""select rowid, * from fts_entries 
               where rowid = ?""", 
               mytuple)
    
    pinned_entry = db.fetchone()
    
    db.execute("""select rowid, * 
               from fts_entries 
               order by rowid 
               desc""")
    
    entries = db.fetchall()
    
    return render_template('tabs.html', 
                           entries = entries, 
                           pinned_entry = pinned_entry)

@app.route('/admin/<url>', methods = ["GET", "POST"])
def admin_show_post(url):
    
    db = g.sqlite_db.cursor()
    
    mytuple = (url, )
    db.execute("select rowid, * from fts_entries where url=?", mytuple)
    entry = db.fetchone()
    return render_template("admin_post.html", entry = entry)

@app.route('/admin/create', methods = ["GET", "POST"])
def create():
    if request.method == "POST":
        if request.form["title"] and request.form["body"] and request.form["lead"]:
            
            db = g.sqlite_db.cursor()
            
            title = request.form.get("title")
            body = request.form.get("body")
            localtime = time.asctime( time.localtime(time.time()) )
            lead = request.form.get("lead")
            url = slugify(title)
            
            if request.form.get("publish") == "publish":
                mytuple = (title, lead, body, 1, localtime, url)
                db.execute("""insert into fts_entries(title, lead, body, published, date, url) values(?, ?, ?, ?, ?, ?)""", mytuple)
                
            if request.form.get("save_for_later") == "save_for_later":
                mytuple = (title, lead, body, 0, localtime, url)
                db.execute("""insert into fts_entries(title, lead, body, published, date, url) values(?, ?, ?, ?, ?, ?)""", mytuple)
                
            flash("Your post has been created successfully")
            get_db().commit()
            return redirect(url_for("admin_posts"))
                    
        else:
            flash("You haven't entered text")
            return render_template('create.html')
    return render_template('create.html')
    
@app.route('/edit', methods=["POST", "GET"])
def edit():
    db = g.sqlite_db.cursor()
    
    if request.method == "POST":
        
        if request.form.get("edit_btn") == "edit":
            entry_id = int(request.form.get("edit_id"))
            mytuple = (entry_id, )
            db.execute("select rowid, * from fts_entries where rowid=?", mytuple)
            entry = db.fetchone()
            return render_template("edit.html", entry=entry)

        # post from home page
        
        elif request.form.get("publish_index") == "publish_index":
            rowid = int(request.form.get("rowid"))
            mydic = { 
                        "published": 1,
                        "rowid": rowid
                    }
            db.execute("""update fts_entries set 
                           published=:published
                           where rowid=:rowid""", mydic)
            flash("Post has been published successfully")
            get_db().commit()
            return redirect(url_for("admin_posts")) 
            
        elif request.form.get("unpublish") == "unpublish":
            rowid = int(request.form.get("rowid"))
            mydic = { 
                    "published": 0,
                    "rowid": rowid
                }
            db.execute("""update fts_entries set 
                       published=:published
                       where rowid=:rowid""", mydic)
            flash("Post has been unpublished successfully")
            get_db().commit()
            return redirect(url_for("admin_posts")) 
        
    else:
        return redirect(url_for("admin_posts"))
    return redirect(url_for("admin_posts"))
        
@app.route("/admin/update", methods=["POST", "GET"])
def update():
    if request.method == "POST":
        
        db = g.sqlite_db.cursor()
        
        rowid = int(request.form.get("rowid"))
        title = request.form.get("title")
        lead = request.form.get("lead")
        body = request.form.get("body")
        
        if request.form.get("edit_delete_btn") == "delete":
            
            mytuple = (rowid, )
            db.execute("delete from fts_entries where rowid=?", mytuple)
            get_db().commit()
            flash("Entry has been deleted successfully")
            return redirect(url_for("admin_posts"))
            
        if request.form.get("publish") == "publish":
            url = slugify(title)
            mydic = {"title": title, 
                     "lead": lead,
                     "body": body,
                     "published": 1,
                     "url": url,
                     "rowid": rowid}
            
            db.execute("""update fts_entries set 
                           title=:title, 
                           lead=:lead,
                           body=:body,
                           published=:published,
                           url=:url
                           where rowid=:rowid""", mydic)
            
            get_db().commit()
            flash("Changes saved successfully")
            return redirect(url_for("admin_show_post", url = url))
            
        if request.form.get("save_for_later") == "save_for_later":
            url = slugify(title)
            mydic = {"title": title, 
                     "lead": lead,
                     "body": body,
                     "published": 0,
                     "url": url,
                     "rowid": rowid}
            
            db.execute("""update fts_entries set 
                           title=:title,
                           lead=:lead, 
                           body=:body,
                           published=:published,
                           url=:url
                           where rowid=:rowid""", mydic)
                           
            get_db().commit()
            flash("Changes saved successfully")
        
        return redirect(url_for("admin_show_post", url = url))
    return redirect(url_for("admin_posts"))

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST" and request.form.get("user_search"):
        
        user_search = request.form.get("user_search")
        
        db = g.sqlite_db.cursor()
    
        # replace !:,":,": with spaces
        user_search = re.sub(r"\W+", " ", user_search)
        
        user_search_array = user_search.split()
        
        for index, word in enumerate(user_search_array):
            # append * to each word
            word = word + "*"
            user_search_array[index] = word
        
        user_search_array = " ".join(user_search_array)
        mytuple = (user_search_array, 1)
        
        # -1 means search all columns, 45 – number of symbols in snippet
        db.execute("""select title, url, snippet(
                   fts_entries, '<b>', '</b>', '...', -1, 63) 
                   from fts_entries 
                   where fts_entries match ? and published = ?
                   """, mytuple)
        entries1 = db.fetchall()
        
        mydict_array = []
        for entry in entries1: 
            new_dict = dict(title = entry[0], url= entry[1], snippet = entry[2])
            mydict_array.append(new_dict)
        
        # this will remove all the html tags except <b> tags: 
        # <(?!b|/b\s*\/?)[^>]+>
        cleanr = re.compile('<(?!b|/b\s*\/?)[^>]+>')
        for index, item in enumerate(mydict_array):
            item["snippet"] = re.sub(cleanr, "", item["snippet"])
            item[index] = item
            
        return render_template("search.html", 
                               entries1 = mydict_array,
                               entries_top_5 = g_top_5())
        
    return redirect(url_for("allposts"))

@app.route('/admin/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == app.password:
            session['logged_in'] = True
            flash("You are logged in")
            return redirect(url_for("admin_posts"))
        else:
            flash("Sorry, wrong password")
            return render_template('login.html')
    return render_template("login.html")

@app.route('/admin/logout', methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        session['logged_in'] = False
        flash('You are logged out')
        return redirect(url_for('login'))

# HOUSEKEEPING (decorators and tools come here)

@app.before_request
def before_request():
    """Opens the database before the request."""
    get_db()
    
# teardown instead of after_request, works even after error
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
