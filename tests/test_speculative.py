#!/usr/bin/env python
# -*- coding: latin-1 -*-
#

from __future__ import print_function

import unittest

from mock import Mock

from hoft import ArgsNotAnalysedError, IGNORE, KeywordError, NOVALUE, NotAnalysedError, \
    PositionalError, analyse_sig
from tests.helpers import check_calls


class _Success(Exception):
    pass


class _Error(Exception):
    pass


class AnalyseSigNoDefaultTestCase(unittest.TestCase):
    def setUp(self):
        self._f_a = Mock()
        self._f_c = Mock()
        self._f_f = Mock()
        self._f_on_error = Mock()

    def tearDown(self):
        pass

    def test_analyse_sig_strict_with_on_error_handler_no_errors(self):
        def f_a(name, index, value):
            self._f_a(name, index, value)
            # print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))

        def f_c(name, index, value):
            self._f_c(name, index, value)
            # print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            # print('f_f: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
            #     name, index, called_with_value, default_value))

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            # print('f_on_error exc:    {0}'.format(str(exc)))
            # print('f_on_error errors: {0}'.format(str(errors)))

        @analyse_sig(
            f_a, IGNORE, f_c,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _on_error_=f_on_error,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        self.assertRaises(_Success, voo, 11, 22, 33, 44, e=99)
        self._f_on_error.assert_called_once()
        cargs = self._f_on_error.call_args_list[0][0]
        self.assertIsInstance(cargs[0], ArgsNotAnalysedError)
        self.assertEqual(set(cargs[0].names), set(['b', 'e', 'g', 'kwargs']))
        self.assertEqual(len(cargs[1]), 1)
        self.assertIsInstance(cargs[1][0], NotAnalysedError)
        self.assertEqual(set(cargs[1][0].name), set(['b', 'e', 'g', 'kwargs']))
        self.assertIs(cargs[1][0].error, cargs[0])

        self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
        self._f_c.assert_called_once_with('c', 2, 33)
        self._f_a.assert_called_once_with('a', 0, 11)

    def test_analyse_sig_strict_without_on_error_handler_fail_slow_no_errors(self):
        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            print('f_on_error exc:    {0}'.format(str(exc)))
            print('f_on_error errors: {0}'.format(str(errors)))

        @analyse_sig(
            f_a, IGNORE, f_c,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            # _on_error_=f_on_error,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except ArgsNotAnalysedError as e:
            self.assertEqual(set(e.names), set(['b', 'e', 'g', 'kwargs']))
            errors = e._errors_
            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)
            print('errors: {0}'.format(errors))
            error = errors[0]
            self.assertIsInstance(error, NotAnalysedError)
            self.assertIsInstance(error.error, ArgsNotAnalysedError)
            self.assertEqual(set(error.name), set(['b', 'e', 'g', 'kwargs']))
            self.assertDictEqual(
                {
                    'a': 11,
                    'b': 22,
                    'c': 33,
                    'd': 44,
                    'e': 99,
                    'f': '2',
                    'g': {3: 4},
                    'kwargs': {},
                },
                error.callargs)
            print(error.callargs)
            self._f_on_error.assert_not_called()
            self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
            self._f_c.assert_called_once_with('c', 2, 33)
            self._f_a.assert_called_once_with('a', 0, 11)
        else:
            assert False

    def test_analyse_sig_strict_without_on_error_handler_fail_slow(self):
        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_f: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))
            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            print('f_on_error exc:    {0}'.format(str(exc)))
            print('f_on_error errors: {0}'.format(str(errors)))

        @analyse_sig(
            f_a, IGNORE, f_c,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'a')
            errors = e._errors_
            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 4)
            # print('errors: {0}'.format(errors))
            error = errors[0]
            self.assertIsInstance(error, PositionalError)
            self.assertEqual(error.name, 'a')
            self.assertEqual(error.func_name, 'f_a')
            self.assertEqual(error.value, 11)
            self.assertEqual(error.index, 0)

            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'a')
            self.assertEqual(len(error.error._errors_), 4)
            print('errors: {0}'.format(error.error._errors_))

            error = errors[1]
            self.assertIsInstance(error, PositionalError)
            self.assertEqual(error.name, 'c')
            self.assertEqual(error.func_name, 'f_c')
            self.assertEqual(error.value, 33)
            self.assertEqual(error.index, 2)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'c')

            error = errors[2]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.name, 'f')
            self.assertEqual(error.func_name, 'f_f')
            self.assertEqual(error.value, NOVALUE)
            self.assertEqual(error.error.message, 'f')
            self.assertEqual(error.name, 'f')
            self.assertEqual(error.default_value, '2')

            error = errors[3]
            self.assertIsInstance(error, NotAnalysedError)
            self.assertEqual(set(error.name), set(['b', 'e', 'g', 'kwargs']))
            self.assertIsInstance(error.error, ArgsNotAnalysedError)
            self.assertEqual(set(error.error.names), set(['b', 'e', 'g', 'kwargs']))

            self._f_on_error.assert_not_called()
            self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
            self._f_c.assert_called_once_with('c', 2, 33)
            self._f_a.assert_called_once_with('a', 0, 11)
        else:
            assert False

    def test_analyse_sig_strict_without_on_error_handler_fail_fast(self):
        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_f: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))
            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            print('f_on_error exc:    {0}'.format(str(exc)))
            print('f_on_error errors: {0}'.format(str(errors)))

        @analyse_sig(
            f_a, IGNORE, f_c,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=True,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'a')
            errors = e._errors_
            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)
            print('errors: {0}'.format(errors))
            error = errors[0]
            self.assertIsInstance(error, PositionalError)
            self.assertEqual(error.func_name, 'f_a')
            self.assertEqual(error.name, 'a')
            self.assertEqual(error.value, 11)
            self.assertIsInstance(error.error, _Error)
            self._f_on_error.assert_not_called()
            self._f_f.assert_not_called()
            self._f_c.assert_not_called()
            self._f_a.assert_called_once_with('a', 0, 11)
        else:
            assert False

    def test_analyse_sig_strict_with_on_error_handler_fail_slow(self):
        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))

            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))

            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            print('f_on_error exc:    {0}'.format(str(exc)))
            print('f_on_error errors: {0}'.format(str(errors)))

            raise _Error('on_error')

        @analyse_sig(
            f_a, IGNORE, f_c,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _on_error_=f_on_error,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'on_error')
            self.assertEqual(self._f_on_error.call_count, 1)

            self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
            self._f_c.assert_called_once_with('c', 2, 33)
            self._f_a.assert_called_once_with('a', 0, 11)
        else:
            assert False

    def test_analyse_sig_strict_with_on_error_handler_fail_fast(self):
        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self.f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))

            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))

            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            print('f_on_error exc:    {0}'.format(str(exc)))
            print('f_on_error errors: {0}'.format(str(errors)))

            raise _Error('on_error')

        @analyse_sig(
            f_a, IGNORE, f_c,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=True,
            _on_error_=f_on_error,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'on_error')
            self.assertEqual(self._f_on_error.call_count, 1)

            cargs = self._f_on_error.call_args_list[0][0]

            self.assertIsInstance(cargs[0], _Error)
            self.assertEqual(cargs[0].message, 'a')
            self.assertEqual(len(cargs[1]), 1)

            err = cargs[1][0]

            self.assertIsInstance(err, PositionalError)
            self.assertEqual(err.func_name, 'f_a')
            self.assertEqual(err.index, 0)
            self.assertEqual(err.name, 'a')
            self.assertEqual(err.value, 11)

            self._f_f.assert_not_called()
            self._f_c.assert_not_called()
            self._f_a.assert_called_once_with('a', 0, 11)
        else:
            assert False

    def test_analyse_sig_not_strict_without_on_error_handler_fail_fast(self):
        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))

            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))

            raise _Error('f')

        @analyse_sig(
            f_a, IGNORE, f_c,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=True,
            _strict_=False,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'a')
            errors = e._errors_
            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)
            print('errors: {0}'.format(errors))
            err = errors[0]
            self.assertIsInstance(err, PositionalError)
            self.assertIsInstance(err.error, _Error)
            self.assertEqual(err.error.message, 'a')
            self.assertEqual(err.func_name, 'f_a')
            self.assertEqual(err.index, 0)
            self.assertEqual(err.name, 'a')
            self.assertEqual(err.value, 11)

            self._f_f.assert_not_called()
            self._f_c.assert_not_called()
            self._f_a.assert_called_once_with('a', 0, 11)
        else:
            assert False

    def test_analyse_sig_not_strict_without_on_error_handler_fail_slow(self):
        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))

            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))

            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            print('f_on_error exc:    {0}'.format(str(exc)))
            print('f_on_error errors: {0}'.format(str(errors)))

            raise _Error('on_error')

        @analyse_sig(
            f_a, IGNORE, f_c,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _strict_=False,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'a')
            self.assertEqual(self._f_on_error.call_count, 0)
            errors = e._errors_
            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 3)
            print('errors: {0}'.format(errors))
            err = errors[0]
            self.assertIsInstance(err, PositionalError)
            self.assertIsInstance(err.error, _Error)
            self.assertEqual(err.error.message, 'a')
            self.assertEqual(err.func_name, 'f_a')
            self.assertEqual(err.index, 0)
            self.assertEqual(err.name, 'a')
            self.assertEqual(err.value, 11)
            print('errors: {0}'.format(errors))

            error = errors[0]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.name, 'a')
            self.assertEqual(error.value, 11)
            self.assertEqual(error.func_name, 'f_a')
            self.assertEqual(error.func, f_a)
            self.assertEqual(error.error.message, 'a')

            error = errors[1]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.name, 'c')
            self.assertEqual(error.value, 33)
            self.assertEqual(error.func_name, 'f_c')
            self.assertEqual(error.func, f_c)
            self.assertEqual(error.error.message, 'c')

            error = errors[2]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.name, 'f')
            self.assertEqual(error.value, NOVALUE)
            self.assertEqual(error.func_name, 'f_f')
            self.assertEqual(error.func, f_f)
            self.assertEqual(error.error.message, 'f')
            self.assertEqual(error.default_value, '2')

            self._f_on_error.assert_not_called()
            self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
            self._f_c.assert_called_once_with('c', 2, 33)
            self._f_a.assert_called_once_with('a', 0, 11)
        else:
            assert False

    def test_analyse_sig_not_strict_with_on_error_handler_fail_slow(self):
        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))

            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))

            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            print('f_on_error exc:    {0}'.format(str(exc)))
            print('f_on_error errors: {0}'.format(str(errors)))

            raise _Error('on_error')

        @analyse_sig(
            f_a, IGNORE, f_c,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _on_error_=f_on_error,
            _strict_=False,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'on_error')
            self.assertEqual(self._f_on_error.call_count, 1)

            cargs = self._f_on_error.call_args_list[0][0]
            self.assertIsInstance(cargs[0], _Error)
            self.assertEqual(cargs[0].message, 'a')
            self.assertEqual(len(cargs[1]), 3)

            err = cargs[1][0]
            self.assertIsInstance(err, PositionalError)
            self.assertEqual(err.func_name, 'f_a')
            self.assertEqual(err.index, 0)
            self.assertEqual(err.name, 'a')
            self.assertEqual(err.value, 11)

            err = cargs[1][1]
            self.assertIsInstance(err, PositionalError)
            self.assertEqual(err.func_name, 'f_c')
            self.assertEqual(err.index, 2)
            self.assertEqual(err.name, 'c')
            self.assertEqual(err.value, 33)

            err = cargs[1][2]
            self.assertIsInstance(err, KeywordError)
            self.assertEqual(err.func_name, 'f_f')
            self.assertEqual(err.func, f_f)
            self.assertEqual(err.name, 'f')
            self.assertEqual(err.value, NOVALUE)
            self.assertEqual(err.default_value, '2')

            self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
            self._f_c.assert_called_once_with('c', 2, 33)
            self._f_a.assert_called_once_with('a', 0, 11)
        else:
            assert False

    def test_analyse_sig_not_strict_with_on_error_handler_fail_fast(self):
        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))

            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))

            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            print('f_on_error exc:    {0}'.format(str(exc)))
            print('f_on_error errors: {0}'.format(str(errors)))

            raise _Error('on_error')

        @analyse_sig(
            f_a, IGNORE, f_c,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=True,
            _on_error_=f_on_error,
            _strict_=False,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'on_error')
            self.assertEqual(self._f_on_error.call_count, 1)

            cargs = self._f_on_error.call_args_list[0][0]
            self.assertIsInstance(cargs[0], _Error)
            self.assertEqual(cargs[0].message, 'a')
            self.assertEqual(len(cargs[1]), 1)

            err = cargs[1][0]
            self.assertIsInstance(err, PositionalError)
            self.assertEqual(err.func_name, 'f_a')
            self.assertEqual(err.index, 0)
            self.assertEqual(err.name, 'a')
            self.assertEqual(err.value, 11)

            self._f_f.assert_not_called()
            self._f_c.assert_not_called()
            self._f_a.assert_called_once_with('a', 0, 11)
        else:
            assert False


class AnalyseSigWithDefaultTestCase(unittest.TestCase):
    def setUp(self):
        self._f_all = Mock()
        self._f_a = Mock()
        self._f_c = Mock()
        self._f_f = Mock()
        self._f_on_error = Mock()

    def test_analyse_sig_strict_with_on_error_handler_no_errors(self):
        def f_all(name, value, arg_spec):
            self._f_all(name, value, arg_spec)
            print('f_all: name: {0}, index:{1}, value: {2}'.format(name, value, arg_spec))

        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print('f_f: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                name, index, called_with_value, default_value))

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            print('f_on_error exc:    {0}'.format(str(exc)))
            print('f_on_error errors: {0}'.format(str(errors)))

        @analyse_sig(
            f_a, IGNORE, f_c,
            _default_=f_all,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _on_error_=f_on_error,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        self.assertRaises(_Success, voo, 11, 22, 33, 44, e=99)
        self._f_on_error.assert_not_called()
        self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
        self._f_c.assert_called_once_with('c', 2, 33)
        self._f_a.assert_called_once_with('a', 0, 11)

        check_calls(
            self,
            self._f_all.call_args_list,
            [
                ('b', 22),
                ('e', 99),
                ('g', {3: 4}),
                ('kwargs', {}),
            ]
        )

    def test_analyse_sig_strict_without_on_error_handler_fail_slow_no_errors(self):
        def f_all(name, value, arg_spec):
            self._f_all(name, value, arg_spec)
            print('f_all: name: {0}, index:{1}, value: {2}'.format(name, value, arg_spec))

        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))

        @analyse_sig(
            f_a, IGNORE, f_c,
            _default_=f_all,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Success as e:
            self._f_on_error.assert_not_called()
            self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
            self._f_c.assert_called_once_with('c', 2, 33)
            self._f_a.assert_called_once_with('a', 0, 11)

            check_calls(
                self,
                self._f_all.call_args_list,
                [
                    ('b', 22),
                    ('e', 99),
                    ('g', {3: 4}),
                    ('kwargs', {}),
                ]
            )
        else:
            assert False

    def test_analyse_sig_strict_without_on_error_handler_fail_slow(self):
        def f_all(name, value, arg_spec):
            self._f_all(name, value, arg_spec)
            print('f_all: name: {0}, index:{1}, value: {2}'.format(name, value, arg_spec))
            raise _Error('all')

        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_f: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))
            raise _Error('f')

        @analyse_sig(
            f_a, IGNORE, f_c,
            _default_=f_all,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            errors = e._errors_
            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 7)

            error = errors[0]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'a')
            self.assertEqual(error.value, 11)
            self.assertEqual(error.func, f_a)
            self.assertEqual(error.func_name, 'f_a')
            self.assertEqual(error.name, 'a')

            error = errors[1]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'c')
            self.assertEqual(error.value, 33)
            self.assertEqual(error.func, f_c)
            self.assertEqual(error.func_name, 'f_c')
            self.assertEqual(error.name, 'c')

            error = errors[2]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'f')
            self.assertEqual(error.value, NOVALUE)
            self.assertEqual(error.func, f_f)
            self.assertEqual(error.func_name, 'f_f')
            self.assertEqual(error.name, 'f')
            self.assertEqual(error.default_value, '2')

            error = errors[3]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'all')
            self.assertEqual(error.func_name, 'f_all')
            self.assertEqual(error.value, 22)
            self.assertEqual(error.func, f_all)
            self.assertEqual(error.name, 'b')
            self.assertEqual(error.index, 1)

            error = errors[4]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'all')
            self.assertEqual(error.func_name, 'f_all')
            self.assertEqual(error.value, 99)
            self.assertEqual(error.func, f_all)
            self.assertEqual(error.name, 'e')
            self.assertEqual(error.default_value, 99)

            error = errors[5]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'all')
            self.assertEqual(error.func_name, 'f_all')
            self.assertEqual(error.value, {3: 4})
            self.assertEqual(error.func, f_all)
            self.assertEqual(error.name, 'g')
            self.assertEqual(error.default_value, {3: 4})

            error = errors[6]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'all')
            self.assertEqual(error.func_name, 'f_all')
            self.assertEqual(error.value, {})
            self.assertEqual(error.func, f_all)
            self.assertEqual(error.name, 'kwargs')
            self.assertEqual(error.default_value, {})

            self._f_on_error.assert_not_called()
            self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
            self._f_c.assert_called_once_with('c', 2, 33)
            self._f_a.assert_called_once_with('a', 0, 11)

            check_calls(
                self,
                self._f_all.call_args_list,
                [
                    ('b', 22),
                    ('e', 99),
                    ('g', {3: 4}),
                    ('kwargs', {}),
                ]
            )
        else:
            assert False

    def test_analyse_sig_strict_without_on_error_handler_fail_fast(self):
        def f_all(name, value, arg_spec):
            self._f_all(name, value, arg_spec)
            print('f_all: name: {0}, index:{1}, value: {2}'.format(
                name, value, arg_spec))
            raise _Error('all')

        def f_a(name, index, value):
            self._f_a(name, index, value)
            print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            print(
                'f_f: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
                    name, index, called_with_value, default_value))
            raise _Error('f')

        @analyse_sig(
            f_a, IGNORE, f_c,
            _default_=f_all,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=True,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            errors = e._errors_
            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)
            error = errors[0]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'a')
            self.assertEqual(error.name, 'a')
            self.assertEqual(error.value, 11)
            self.assertEqual(error.index, 0)
            self.assertEqual(error.func_name, 'f_a')
            self.assertEqual(error.func, f_a)

            self._f_on_error.assert_not_called()
            self._f_f.assert_not_called()
            self._f_c.assert_not_called()
            self._f_a.assert_called_once_with('a', 0, 11)
            self._f_all.assert_not_called()
        else:
            assert False

    # FIXME: BELOW HERE.

    def test_analyse_sig_strict_with_on_error_handler_fail_slow(self):
        def f_all(name, value, arg_spec):
            self._f_all(name, value, arg_spec)
            # print('f_all: name: {0}, index:{1}, value: {2}'.format(name, value, arg_spec))
            raise _Error('all')

        def f_a(name, index, value):
            self._f_a(name, index, value)
            # print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            # print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            # print(
            #     'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
            #         name, index, called_with_value, default_value))
            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            # print('f_on_error exc:    {0}'.format(str(exc)))
            # print('f_on_error errors: {0}'.format(str(errors)))
            raise _Error('on_error')

        @analyse_sig(
            f_a, IGNORE, f_c,
            _default_=f_all,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _on_error_=f_on_error,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'on_error')
            self.assertEqual(self._f_on_error.call_count, 1)
            self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
            self._f_c.assert_called_once_with('c', 2, 33)
            self._f_a.assert_called_once_with('a', 0, 11)
            self.assertEqual(self._f_all.call_count, 4)

            check_calls(
                self,
                self._f_all.call_args_list,
                [
                    ('b', 22),
                    ('e', 99),
                    ('g', {3: 4}),
                    ('kwargs', {}),
                ]
            )
        else:
            assert False

    def test_analyse_sig_strict_with_on_error_handler_fail_fast(self):
        def f_all(name, value, arg_spec):
            self._f_all(name, value, arg_spec)
            # print('f_all: name: {0}, index:{1}, value: {2}'.format(name, value, arg_spec))
            raise _Error('all')

        def f_a(name, index, value):
            self._f_a(name, index, value)
            # print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            # print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            # print(
            #     'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
            #         name, index, called_with_value, default_value))
            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            # print('f_on_error exc:    {0}'.format(str(exc)))
            # print('f_on_error errors: {0}'.format(str(errors)))
            raise _Error('on_error')

        @analyse_sig(
            f_a, IGNORE, f_c,
            _default_=f_all,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=True,
            _on_error_=f_on_error,
            _strict_=True,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'on_error')
            self.assertEqual(self._f_on_error.call_count, 1)
            self._f_f.assert_not_called()
            self._f_c.assert_not_called()
            self._f_a.assert_called_once_with('a', 0, 11)
            self._f_all.assert_not_called()
        else:
            assert False

    def test_analyse_sig_not_strict_without_on_error_handler_fail_fast(self):
        def f_all(name, value, arg_spec):
            self._f_all(name, value, arg_spec)
            # print('f_all: name: {0}, index:{1}, value: {2}'.format(name, value, arg_spec))
            raise _Error('all')

        def f_a(name, index, value):
            self._f_a(name, index, value)
            # print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            # print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            # print(
            #     'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
            #         name, index, called_with_value, default_value))
            raise _Error('f')

        @analyse_sig(
            f_a, IGNORE, f_c,
            _default_=f_all,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=True,
            _strict_=False,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            errors = e._errors_
            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 1)
            error = errors[0]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'a')
            self._f_f.assert_not_called()
            self._f_c.assert_not_called()
            self._f_a.assert_called_once_with('a', 0, 11)
            self._f_all.assert_not_called()
        else:
            assert False

    def test_analyse_sig_not_strict_without_on_error_handler_fail_slow(self):
        def f_all(name, value, arg_spec):
            self._f_all(name, value, arg_spec)
            # print('f_all: name: {0}, index:{1}, value: {2}'.format(name, value, arg_spec))
            raise _Error('all')

        def f_a(name, index, value):
            self._f_a(name, index, value)
            # print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            # print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            # print(
            #     'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
            #         name, index, called_with_value, default_value))
            raise _Error('f')

        @analyse_sig(
            f_a, IGNORE, f_c,
            _default_=f_all,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _strict_=False,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            errors = e._errors_
            self.assertIsInstance(errors, list)
            self.assertEqual(len(errors), 7)

            error = errors[0]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'a')

            error = errors[1]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'c')

            error = errors[2]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'f')
            self.assertEqual(error.func_name, 'f_f')
            self.assertEqual(error.value, NOVALUE)
            self.assertEqual(error.func, f_f)
            self.assertEqual(error.name, 'f')

            error = errors[3]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'all')
            self.assertEqual(error.func_name, 'f_all')
            self.assertEqual(error.value, 22)
            self.assertEqual(error.func, f_all)
            self.assertEqual(error.name, 'b')
            self.assertEqual(error.index, 1)

            error = errors[4]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'all')
            self.assertEqual(error.func_name, 'f_all')
            self.assertEqual(error.value, 99)
            self.assertEqual(error.func, f_all)
            self.assertEqual(error.name, 'e')

            error = errors[5]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'all')
            self.assertEqual(error.func_name, 'f_all')
            self.assertEqual(error.value, {3: 4})
            self.assertEqual(error.func, f_all)
            self.assertEqual(error.name, 'g')

            error = errors[6]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _Error)
            self.assertEqual(error.error.message, 'all')
            self.assertEqual(error.func_name, 'f_all')
            self.assertEqual(error.value, {})
            self.assertEqual(error.func, f_all)
            self.assertEqual(error.name, 'kwargs')

            self._f_on_error.assert_not_called()
            self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
            self._f_c.assert_called_once_with('c', 2, 33)
            self._f_a.assert_called_once_with('a', 0, 11)

            self.assertEqual(self._f_all.call_count, 4)
            calls = self._f_all.call_args_list
            self.assertEqual(len(calls), 4)
            call = calls[0]
            self.assertEqual(call[0][0], 'b')
            self.assertEqual(call[0][1], 22)

            call = calls[1]
            self.assertEqual(call[0][0], 'e')
            self.assertEqual(call[0][1], 99)

            call = calls[2]
            self.assertEqual(call[0][0], 'g')
            self.assertEqual(call[0][1], {3: 4})

            call = calls[3]
            self.assertEqual(call[0][0], 'kwargs')
            self.assertEqual(call[0][1], {})
        else:
            assert False

    def test_analyse_sig_not_strict_with_on_error_handler_fail_slow(self):
        def f_all(name, value, arg_spec):
            self._f_all(name, value, arg_spec)
            # print('f_all: name: {0}, index:{1}, value: {2}'.format(name, value, arg_spec))
            raise _Error('all')

        def f_a(name, index, value):
            self._f_a(name, index, value)
            # print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            # print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            # print(
            #     'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
            #         name, index, called_with_value, default_value))
            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            print('f_on_error exc:    {0}'.format(str(exc)))
            print('f_on_error errors: {0}'.format(str(errors)))

            raise _Error('on_error')

        @analyse_sig(
            f_a, IGNORE, f_c,
            _default_=f_all,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=False,
            _on_error_=f_on_error,
            _strict_=False,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'on_error')
            self.assertEqual(self._f_on_error.call_count, 1)
            self._f_f.assert_called_once_with('f', 5, NOVALUE, '2')
            self._f_c.assert_called_once_with('c', 2, 33)
            self._f_a.assert_called_once_with('a', 0, 11)
            self.assertEqual(self._f_all.call_count, 4)
        else:
            assert False

    def test_analyse_sig_not_strict_with_on_error_handler_fail_fast(self):
        def f_all(name, value, arg_spec):
            self._f_all(name, value, arg_spec)
            # print('f_all: name: {0}, index:{1}, value: {2}'.format(name, value, arg_spec))
            raise _Error('all')

        def f_a(name, index, value):
            self._f_a(name, index, value)
            # print('f_a: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('a')

        def f_c(name, index, value):
            self._f_c(name, index, value)
            # print('f_c: name: {0}, index:{1}, value: {2}'.format(name, index, value))
            raise _Error('c')

        def f_f(name, index, called_with_value, default_value):
            self._f_f(name, index, called_with_value, default_value)
            # print(
            #     'f_c: name: {0}, index:{1}, called_with_value: {2}, default_value: {3}'.format(
            #         name, index, called_with_value, default_value))
            raise _Error('f')

        def f_on_error(exc, errors):
            self._f_on_error(exc, errors)
            # print('f_on_error exc:    {0}'.format(str(exc)))
            # print('f_on_error errors: {0}'.format(str(errors)))
            raise _Error('on_error')

        @analyse_sig(
            f_a, IGNORE, f_c,
            _default_=f_all,
            c=IGNORE, d=IGNORE, f=f_f,
            _fail_fast_=True,
            _on_error_=f_on_error,
            _strict_=False,
        )
        def voo(a, b, c, d, e=1, f='2', g={3: 4}, **kwargs):
            raise _Success()

        try:
            voo(11, 22, 33, 44, e=99)
        except _Error as e:
            self.assertEqual(e.message, 'on_error')
            self.assertEqual(self._f_on_error.call_count, 1)
            self._f_f.assert_not_called()
            self._f_c.assert_not_called()
            self._f_a.assert_called_once_with('a', 0, 11)
            self._f_all.assert_not_called()
        else:
            assert False


if __name__ == '__main__':
    unittest.main()
