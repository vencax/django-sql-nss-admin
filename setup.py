#!/usr/bin/env python
import os

from setuptools import setup, find_packages


README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'README')

description = 'DJango module for SQL based Linux NSS authentication system'

if os.path.exists(README_PATH):
    long_description = open(README_PATH).read()
else:
    long_description = description

setup(name='django-sql-nss-admin',
    version='0.3',
    description=description,
    license='BSD',
    url='https://github.com/vencax/django-sql-nss-admin',
    author='vencax',
    author_email='info@vxk.cz',
    packages=find_packages(),
    install_requires=[
        'django>=1.3',
    ],
    keywords="django linux libnss-mysql nss admin",
    include_package_data=True,
)
