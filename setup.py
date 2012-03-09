#!/usr/bin/env python
from setuptools import setup, find_packages
import os

README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README')

description = 'Admininstration module for SQL based Linux NSS authentication system'

if os.path.exists(README_PATH):
    long_description = open(README_PATH).read()
else:
    long_description = description

setup(name='django-sql-nss-admin',
    version='0.1',
    description=description,
    license='BSD',
    url='https://github.com/vencax/django-vxk-forum',
    author='vencax',
    author_email='vencax@centrum.cz',
    packages=find_packages(),
    install_requires=[
        'django>=1.3',
        'git://github.com/vencax/django-command-runner.git'
    ],
    keywords="django linux libnss-mysql nss admin",
    include_package_data=True,
)
