# -*- coding: utf-8 -*-

from setuptools import setup

# http://flask.pocoo.org/docs/0.12/patterns/packages/ for documentation

setup(
    name = "blog",
    packages = ['blog'],
    include_package_data = True,
    install_requires = [
        'flask',
        'flask_wtf',
        'flask_mail',
        'unidecode',
    ],
)
