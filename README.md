# Shiba-Inu Blog

Semantic UI blog template with backend in Python and Flask. Has a subscription block with a mail server, in-house full-text search engine and top-5 section. Shiba-Inu logos are made via Illustrator and cannot be used without permission.

## CS50

This blog was initially made as a final project for the Harvard University [CS50](https://cs50.harvard.edu) programming course.

## Preview

Post example:

![Alt text](blog/static/images/blog_post.jpg?raw=true)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installing

Download the repository manually or run:

```
$ git clone https://github.com/joliejuly/blog.git
```
Files should be installed as a package:

```
$ cd blog
$ export FLASK_APP=blog
$ export FLASK_DEBUG=true
$ pip3 install -e .
$ flask run
```

For further information check Flask documentation – http://flask.pocoo.org/docs/0.12/patterns/packages/

## Usage

### Admin Page

Access admin page via **/admin_posts** URL.
Password is stored as **app.password** variable inside __init.py__ module. Change it and store as an environment variable for security purposes.

**Text editor** for posts – [Tiny MCE](https://www.tinymce.com)

![Alt text](blog/static/images/blog_admin.jpg?raw=true)

### Mail Server

This blog has a subscription feature, which runs using flask_mail server. It's all set up.
Inside __init.py__ module insert your mail settings:
```
app.config['MAIL_SERVER'] = 'smtp.yourhost.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "username@yourhost.com"
app.config['MAIL_PASSWORD'] = "password"
```
Mail is sent asynchronously.

## Key Features

### Search Engine

Blog has an in-house full-text search engine, built using FTS4 SQLite extention. You can find not only keywords, but sentences and phrases.

![Alt text](blog/static/images/blog_search.jpg?raw=true)

### URL Slugify

Slugify function allows you to dynamically generate urls like "how-to-choose-your-shiba-inu". It also supports cyrillic headers – they are translated into latin alphabet.

## Built With

* Flask
* SQLite3
* Semantic UI

## Authors

* **Julia Nikitina** - [joliejuly](https://github.com/joliejuly)

## License

This project is licensed under the MIT License - see the [LICENSE.md](/LICENSE.md) file for details
This license is not covering illustrations and logos – copyrighted and restricted use without permission.
