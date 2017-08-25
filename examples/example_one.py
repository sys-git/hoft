#!/usr/bin/env python
# -*- coding: latin-1 -*-
# pylint: skip-file

from __future__ import print_function

import six
from hoft import analyse_in, IGNORE


# This signature is used for positional args:
def validate_unicode(value, index):
    if not isinstance(value, unicode):
        raise TypeError('Positional param at index {i} not a unicode string'.format(
            i=index))


# This signature is used for keyword args:
def validate_weight(value, name, present):
    print('keyword param {n} is {p}present in the callers params'.format(
        n=name, p='' if present else 'not '))

    if not isinstance(value, six.integer_types):
        raise TypeError('{n} is not an integer'.format(name))


@analyse_in(validate_unicode, validate_unicode, age=IGNORE, ignored=None, weight=validate_weight)
def my_webserver_handler(firstname, lastname, age=None, weight=None):
    pass


result = my_webserver_handler('Billy', 'Bob', age=101, _fail_fast=False)
print(result)
