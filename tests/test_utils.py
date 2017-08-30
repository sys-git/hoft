#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

import functools
import unittest
from inspect import getargspec

from hoft.core.utils import (
    NoDefaultError, Signature, get_func_name,
)
from hoft.core.sigs import get_signature, get_default_value


class Test(unittest.TestCase):
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


class ArgSpecTestCase(unittest.TestCase):
    def test_args(self):
        def voo(a, b):
            pass

        argspec = getargspec(voo)
        e_sig = Signature(['a', 'b'], None, {}, None)
        sig = get_signature(argspec)

        self.assertEqual(sig, e_sig)

    def test_keywords(self):
        def voo(a=1, b=2):
            pass

        argspec = getargspec(voo)
        e_sig = Signature([], None, {'a': 1, 'b': 2}, None)
        sig = get_signature(argspec)

        self.assertEqual(sig, e_sig)
        self.assertEqual(get_default_value('a', argspec), 1)
        self.assertEqual(get_default_value('b', argspec), 2)

    def test_args_and_varargs(self):
        def voo(a, b, *c):
            pass

        argspec = getargspec(voo)
        e_sig = Signature(['a', 'b'], 'c', {}, None)
        sig = get_signature(argspec)

        self.assertEqual(sig, e_sig)
        self.assertRaises(NoDefaultError, get_default_value, 'a', argspec)
        self.assertRaises(NoDefaultError, get_default_value, 'b', argspec)
        self.assertRaises(NoDefaultError, get_default_value, 'c', argspec)

    def test_args_and_keywords(self):
        def voo(a, b, d=3, e=4):
            pass

        argspec = getargspec(voo)
        e_sig = Signature(['a', 'b'], None, {'d': 3, 'e': 4}, None)
        sig = get_signature(argspec)

        self.assertEqual(sig, e_sig)
        self.assertRaises(NoDefaultError, get_default_value, 'a', argspec)
        self.assertRaises(NoDefaultError, get_default_value, 'b', argspec)
        self.assertEqual(get_default_value('d', argspec), 3)
        self.assertEqual(get_default_value('e', argspec), 4)

    def test_varargs_and_kwargs(self):
        def voo(*a, **b):
            pass

        argspec = getargspec(voo)
        e_sig = Signature([], 'a', {}, 'b')
        sig = get_signature(argspec)

        self.assertEqual(sig, e_sig)
        self.assertRaises(NoDefaultError, get_default_value, 'a', argspec)
        self.assertRaises(NoDefaultError, get_default_value, 'b', argspec)

    def test_keywords_and_kwargs(self):
        def voo(a=1, **b):
            pass

        argspec = getargspec(voo)
        e_sig = Signature([], None, {'a': 1}, 'b')
        sig = get_signature(argspec)

        self.assertEqual(sig, e_sig)
        self.assertEqual(get_default_value('a', argspec), 1)
        self.assertRaises(NoDefaultError, get_default_value, 'b', argspec)


if __name__ == '__main__':
    unittest.main()
