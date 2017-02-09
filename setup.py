# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    with open(path) as f:
        return f.read()

setup(
    name='luizalabs-django-toolkit',
    version='1.3.4',
    description=(
        'The LuizaLabs set of tools '
        'to develop projects using the Django framework'
    ),
    long_description=read('README.rst'),
    author='Luizalabs',
    author_email='pypi@luizalabs.com',
    url='https://github.com/luizalabs/django-toolkit',
    keywords='django tools logs middleware utils',
    install_requires=[
        'Django>=1.8',
    ],
    extras_require={
        'oauth2': ['django-oauth-toolkit'],
    },
    packages=find_packages(exclude=[
        'tests*'
    ]),
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)
