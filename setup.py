#!/usr/bin/env python
# -*- coding: latin-1 -*-

#   __                 ___ __
#  /\ \              /'___/\ \__
#  \ \ \___     ___ /\ \__\ \ ,_\
#   \ \  _ `\  / __`\ \ ,__\ \ \/
#    \ \ \ \ \/\ \L\ \ \ \_/\ \ \_
#     \ \_\ \_\ \____/\ \_\  \ \__\
#      \/_/\/_/\/___/  \/_/   \/__/
#
import os
import sys

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'hoft', '__version__.py')) as f:
    exec (f.read(), about)

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    # os.system('python setup.py sdist bdist_wheel')
    # os.system('twine upload dist/*')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (
    about['__version__'], about['__version__']))
    print("  git push --tags")
    sys.exit()
elif sys.argv[-1] == 'test':
    os.system('make test')
    sys.exit()

requires = [
    'six',
    'pip',
    'enum34',
]

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=['hoft', 'hoft/core'],
    license=about['__license__'],
    requires=requires,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
