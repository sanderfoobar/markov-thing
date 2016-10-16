#!/usr/bin/env python

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='markov-thing',
    version='1.0',
    description='Generate markov text - Hard fork of github.com/codebox/markov-text/',
    author='Sander Ferdinand',
    author_email='sa.ferdinand@gmail.com',
    url='https://github.com/skftn/markov-thing/',
    packages=['markov_thing'],
    entry_points={
        'console_scripts': [
            'markov_thing = markov_thing.markov:main'
        ]
    },
    license="MIT",
    keywords="markov",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
