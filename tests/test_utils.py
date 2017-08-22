#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Brief description
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

# from nose_parameterized import parameterized
import functools

import unittest2

from hoft.core.utils import get_func_name


class Test(unittest2.TestCase):
    def test_get_func_name_simple(self):
        def my_func():
            pass

        self.assertEqual(get_func_name(my_func), 'my_func')

    def test_decorated_func(self):
        def d(func):
            @functools.wraps(func)
            def _inner():
                pass

            return _inner

        @d
        def my_func():
            pass

        self.assertEqual(get_func_name(my_func), 'my_func')

    def test_multiply_decorated_func(self):
        def d(func1):
            @functools.wraps(func1)
            def _inner1():
                pass

            return _inner1

        def e(func2):
            @functools.wraps(func2)
            def _inner2():
                pass

            return _inner2

        @d
        @e
        def my_func():
            pass

        self.assertEqual(get_func_name(my_func), 'my_func')


if __name__ == '__main__':
    unittest2.main()
