#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Brief description
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

import unittest2
from mock import Mock

from hoft import IGNORE, KeywordError, PositionalError, analyse_in


class _SuccessError(Exception):
    pass


class _FailureError(Exception):
    pass


class _FailureError1(Exception):
    pass


class _OnError(Exception):
    pass


class Test(unittest2.TestCase):
    def test_simple_no_errors(self):
        func_a = Mock()
        func_b = Mock()
        on_error = Mock()

        value_foo = '.foo'
        name_bar = 'bar'
        value_bar = '.bar'
        value_ignored = '.ignored'
        name_baz = 'baz'
        value_baz = '.baz'

        @analyse_in(func_a, IGNORE, bar=func_b, baz=IGNORE, _on_error_=on_error, _fail_fast_=True)
        def decorated_func_a(foo, ignored, bar=None, baz=None):
            assert foo == value_foo
            assert ignored == value_ignored
            assert bar == value_bar
            assert baz == value_baz
            raise _SuccessError()

        args = [value_foo, value_ignored]
        kwargs = {name_bar: value_bar, name_baz: value_baz}

        self.assertRaises(_SuccessError, decorated_func_a, *args, **kwargs)
        func_a.assert_called_once_with(value=value_foo, index=0)
        func_b.assert_called_once_with(name=name_bar, value=value_bar, present=True)
        on_error.assert_not_called()

    def test_simple_on_error_no_handler_fail_fast(self):
        _func_a = Mock(side_effect=_FailureError())
        _func_b = Mock(side_effect=_FailureError1())

        value_foo = '.foo'
        name_bar = 'bar'
        value_ignored = '.ignored'
        value_bar = '.bar'
        name_baz = 'baz'
        value_baz = '.baz'

        def func_a(*args, **kwargs):
            return _func_a(*args, **kwargs)

        def func_b(*args, **kwargs):
            return _func_b(*args, **kwargs)

        @analyse_in(func_a, IGNORE, bar=func_b, baz=IGNORE, _fail_fast_=True)
        def decorated_func_a(foo, ignored, bar=None, baz=None):
            assert foo == value_foo
            assert ignored == value_ignored
            assert bar == value_bar
            assert baz == value_baz
            raise _SuccessError()

        args = [value_foo, value_ignored]
        kwargs = {name_bar: value_bar, name_baz: value_baz}

        try:
            decorated_func_a(*args, **kwargs)
        except _FailureError as exc:
            _func_a.assert_called_once_with(value=value_foo, index=0)
            _func_b.assert_not_called()
            self.assertEqual(len(exc._errors_), 1)

            error = exc._errors_[0]
            self.assertIsInstance(error, PositionalError)
            self.assertIs(error.error, exc)
            self.assertEqual(error.index, 0)
            self.assertEqual(error.value, value_foo)
            self.assertEqual(error.func_name, 'func_a')
            self.assertEqual(error.func, func_a)
        else:
            self.assertFalse(True)

    def test_simple_on_error_no_handler_fail_slow(self):
        _func_a = Mock(side_effect=_FailureError())
        _func_b = Mock(side_effect=_FailureError1())

        value_foo = '.foo'
        name_bar = 'bar'
        value_ignored = '.ignored'
        value_bar = '.bar'
        name_baz = 'baz'
        value_baz = '.baz'

        def func_a(*args, **kwargs):
            return _func_a(*args, **kwargs)

        def func_b(*args, **kwargs):
            return _func_b(*args, **kwargs)

        @analyse_in(func_a, IGNORE, bar=func_b, baz=IGNORE, _fail_fast_=False)
        def decorated_func_a(foo, ignored, bar=None, baz=None):
            assert foo == value_foo
            assert ignored == value_ignored
            assert bar == value_bar
            assert baz == value_baz
            raise _SuccessError()

        args = [value_foo, value_ignored]
        kwargs = {name_bar: value_bar, name_baz: value_baz}

        try:
            decorated_func_a(*args, **kwargs)
        except _FailureError as exc:
            _func_a.assert_called_once_with(value=value_foo, index=0)
            _func_b.assert_called_once_with(name=name_bar, value=value_bar, present=True)
            self.assertEqual(len(exc._errors_), 2)

            error = exc._errors_[0]
            self.assertIsInstance(error, PositionalError)
            self.assertEqual(error.index, 0)
            self.assertEqual(error.value, value_foo)
            self.assertEqual(error.func_name, 'func_a')
            self.assertEqual(error.func, func_a)

            error = exc._errors_[1]
            self.assertIsInstance(error, KeywordError)
            self.assertEqual(error.value, value_bar)
            self.assertEqual(error.func_name, 'func_b')
            self.assertEqual(error.func, func_b)
        else:
            self.assertFalse(True)

    def test_simple_on_error_fail_fast_with_handler_that_raises(self):
        _func_a = Mock(side_effect=_FailureError())
        _func_b = Mock(side_effect=_FailureError1())
        oe = _OnError()
        _func_oe = Mock(side_effect=oe)

        value_foo = '.foo'
        name_bar = 'bar'
        value_ignored = '.ignored'
        value_bar = '.bar'
        name_baz = 'baz'
        value_baz = '.baz'

        def func_a(*args, **kwargs):
            return _func_a(*args, **kwargs)

        def func_b(*args, **kwargs):
            return _func_b(*args, **kwargs)

        def func_oe(*args, **kwargs):
            return _func_oe(*args, **kwargs)

        @analyse_in(func_a, IGNORE, bar=func_b, baz=IGNORE, _fail_fast_=True, _on_error_=func_oe)
        def decorated_func_a(foo, ignored, bar=None, baz=None):
            assert foo == value_foo
            assert ignored == value_ignored
            assert bar == value_bar
            assert baz == value_baz
            raise _SuccessError()

        args = [value_foo, value_ignored]
        kwargs = {name_bar: value_bar, name_baz: value_baz}

        try:
            decorated_func_a(*args, **kwargs)
        except _OnError as exc:
            _func_a.assert_called_once_with(value=value_foo, index=0)
            _func_b.assert_not_called()
            _func_oe.assert_called_once()

            call_args_list = _func_oe.call_args_list
            self.assertEqual(len(call_args_list), 1)

            call_args = call_args_list[0]
            self.assertIsInstance(call_args[0][0], _FailureError)

            errors = call_args[0][1]
            self.assertEqual(len(errors), 1)

            error = errors[0]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _FailureError)
            self.assertEqual(error.index, 0)
            self.assertEqual(error.value, value_foo)
            self.assertEqual(error.func_name, 'func_a')
            self.assertEqual(error.func, func_a)
        else:
            self.assertFalse(True)

    def test_simple_on_error_fail_fast_with_handler_that_does_not_raise(self):
        _func_a = Mock(side_effect=_FailureError())
        _func_b = Mock(side_effect=_FailureError1())
        _func_oe = Mock(return_value='ignored return value')

        value_foo = '.foo'
        name_bar = 'bar'
        value_ignored = '.ignored'
        value_bar = '.bar'
        name_baz = 'baz'
        value_baz = '.baz'

        def func_a(*args, **kwargs):
            return _func_a(*args, **kwargs)

        def func_b(*args, **kwargs):
            return _func_b(*args, **kwargs)

        def func_oe(*args, **kwargs):
            return _func_oe(*args, **kwargs)

        @analyse_in(func_a, IGNORE, bar=func_b, baz=IGNORE, _fail_fast_=True, _on_error_=func_oe)
        def decorated_func_a(foo, ignored, bar=None, baz=None):
            assert foo == value_foo
            assert ignored == value_ignored
            assert bar == value_bar
            assert baz == value_baz
            raise _SuccessError()

        args = [value_foo, value_ignored]
        kwargs = {name_bar: value_bar, name_baz: value_baz}

        self.assertRaises(_SuccessError, decorated_func_a, *args, **kwargs)
        _func_a.assert_called_once_with(value=value_foo, index=0)
        _func_b.assert_called_once_with(name=name_bar, value=value_bar, present=True)
        self.assertEqual(_func_oe.call_count, 2)

        call_args_list = _func_oe.call_args_list
        self.assertEqual(len(call_args_list), 2)

        for call_args, error_type in zip(call_args_list, [_FailureError, _FailureError1]):
            self.assertIsInstance(call_args[0][0], error_type)

            errors = call_args[0][1]
            self.assertEqual(len(errors), 2)

            error = errors[0]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _FailureError)
            self.assertEqual(error.index, 0)
            self.assertEqual(error.value, value_foo)
            self.assertEqual(error.func_name, 'func_a')
            self.assertEqual(error.func, func_a)

            error = errors[1]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _FailureError1)
            self.assertEqual(error.value, value_bar)
            self.assertEqual(error.func_name, 'func_b')
            self.assertEqual(error.func, func_b)

    def test_simple_on_error_fail_slow_with_handler_that_raises(self):
        _func_a = Mock(side_effect=_FailureError())
        _func_b = Mock(side_effect=_FailureError1())
        oe = _OnError()
        _func_oe = Mock(side_effect=oe)

        value_foo = '.foo'
        name_bar = 'bar'
        value_ignored = '.ignored'
        value_bar = '.bar'
        name_baz = 'baz'
        value_baz = '.baz'

        def func_a(*args, **kwargs):
            return _func_a(*args, **kwargs)

        def func_b(*args, **kwargs):
            return _func_b(*args, **kwargs)

        def func_oe(*args, **kwargs):
            return _func_oe(*args, **kwargs)

        @analyse_in(func_a, IGNORE, bar=func_b, baz=IGNORE, _fail_fast_=False, _on_error_=func_oe)
        def decorated_func_a(foo, ignored, bar=None, baz=None):
            assert foo == value_foo
            assert ignored == value_ignored
            assert bar == value_bar
            assert baz == value_baz
            raise _SuccessError()

        args = [value_foo, value_ignored]
        kwargs = {name_bar: value_bar, name_baz: value_baz}

        try:
            decorated_func_a(*args, **kwargs)
        except _OnError:
            _func_a.assert_called_once_with(value=value_foo, index=0)
            _func_b.assert_called_once_with(name=name_bar, value=value_bar, present=True)
            _func_oe.assert_called_once()

            call_args_list = _func_oe.call_args_list
            self.assertEqual(len(call_args_list), 1)

            call_args = call_args_list[0]
            self.assertIsInstance(call_args[0][0], _FailureError)

            errors = call_args[0][1]
            self.assertEqual(len(errors), 2)

            error = errors[0]
            self.assertIsInstance(error, PositionalError)
            self.assertIsInstance(error.error, _FailureError)
            self.assertEqual(error.index, 0)
            self.assertEqual(error.value, value_foo)
            self.assertEqual(error.func_name, 'func_a')
            self.assertEqual(error.func, func_a)

            error = errors[1]
            self.assertIsInstance(error, KeywordError)
            self.assertIsInstance(error.error, _FailureError1)
            self.assertEqual(error.value, value_bar)
            self.assertEqual(error.func_name, 'func_b')
            self.assertEqual(error.func, func_b)
        else:
            self.assertFalse(True)

    def test_simple_on_error_fail_slow_with_handler_that_does_not_raise(self):
        _func_a = Mock(side_effect=_FailureError())
        _func_b = Mock(side_effect=_FailureError1())
        _func_oe = Mock(return_value='ignored return value')

        value_foo = '.foo'
        name_bar = 'bar'
        value_ignored = '.ignored'
        value_bar = '.bar'
        name_baz = 'baz'
        value_baz = '.baz'

        def func_a(*args, **kwargs):
            return _func_a(*args, **kwargs)

        def func_b(*args, **kwargs):
            return _func_b(*args, **kwargs)

        def func_oe(*args, **kwargs):
            return _func_oe(*args, **kwargs)

        @analyse_in(func_a, IGNORE, bar=func_b, baz=IGNORE, _fail_fast_=False, _on_error_=func_oe)
        def decorated_func_a(foo, ignored, bar=None, baz=None):
            assert foo == value_foo
            assert ignored == value_ignored
            assert bar == value_bar
            assert baz == value_baz
            raise _SuccessError()

        args = [value_foo, value_ignored]
        kwargs = {name_bar: value_bar, name_baz: value_baz}

        self.assertRaises(_SuccessError, decorated_func_a, *args, **kwargs)
        _func_a.assert_called_once_with(value=value_foo, index=0)
        _func_b.assert_called_once_with(name=name_bar, value=value_bar, present=True)
        self.assertEqual(_func_oe.call_count, 1)

        call_args_list = _func_oe.call_args_list
        self.assertEqual(len(call_args_list), 1)

        call_args = call_args_list[0]
        self.assertIsInstance(call_args[0][0], _FailureError)

        errors = call_args[0][1]
        self.assertEqual(len(errors), 2)

        error = errors[0]
        self.assertIsInstance(error, PositionalError)
        self.assertIsInstance(error.error, _FailureError)
        self.assertEqual(error.index, 0)
        self.assertEqual(error.value, value_foo)
        self.assertEqual(error.func_name, 'func_a')
        self.assertEqual(error.func, func_a)

        error = errors[1]
        self.assertIsInstance(error, KeywordError)
        self.assertIsInstance(error.error, _FailureError1)
        self.assertEqual(error.value, value_bar)
        self.assertEqual(error.func_name, 'func_b')
        self.assertEqual(error.func, func_b)


if __name__ == '__main__':
    unittest2.main()
