#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Brief description
# @module hoft.core.decorators
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

from inspect import getargspec, getcallargs

import six

from hoft.core.parsers_in import parse_all_in_args
from hoft.core.parsers_sig import parse_all_sig_args
from hoft.core.utils import raise_exc


def analyse_in(*parse_args, **parse_kwargs):
    """
    Decorator for methods (to analyse) the args and kwargs of the decorated callable.
    This method does not modify the args or kwargs in any way.

    :param parse_args: A list of callables which accept two values only:
    These callables will be passed the target function's argument at the same position as - the
    callable is in the decorator's arguments list and the index of the argument.
    If callable==IGNORE, then the decorated function's arg is not parsed.
    :param parse_kwargs: A dictionary of name, callables. The name represents the target
    function's kwarg that will be passed to the callable. The callable receives the name,
    value and a boolean representing if the name is present in the kwargs:
    ie: `def my_func(name, value, name_in_decorated_funcs_passed_kwargs)`.
    :param bool parse_kwargs['_fail_fast_']: True: Fail on the first exception raised by any
    supplied callable.
    :param bool parse_kwargs['_on_error_']: Callable or type to be called when an exception is found
    in a supplied callable, if the type is an exception or subclass-of, it will be raised (the
    exception constructor should take the same signature as my_func below):
    ie: `def my_func(exc, list_of_excs)`.
    If the type is not an exception or subclass-of it will be called, it is up to this callable to
    raise an exception if required.
    :returns: Decorated function.
    :note: Any exception raised by a supplied callable will have an additional field: `_errors_`.
    This is always a list of one or all of the errors encountered during the supplied callables (
    depending on the value of the `_fail_fast_` kwargs.

    Example:
    @hoft.analyse_in(
        _a_func(z=1), None, bar=_b_func(x=1, y=2), baz=_validate_baz(), x=None,
        _fail_fast_=True, _on_error_=my_func,
    )
    def _validate_something_decorated(foo, ignored, bar=hoft.IGNORE, baz=None, x=None):
        ...

    """

    def decorator(func):
        @six.wraps(func)
        def wrapper(*args, **kwargs):
            fail_fast = parse_kwargs.pop('_fail_fast_', False)
            on_error = parse_kwargs.pop('_on_error_', None)

            argspec = getargspec(func)

            errors = parse_all_in_args(
                parse_args,
                parse_kwargs,
                args,
                kwargs,
                argspec,
                on_error,
                fail_fast,
            )

            if errors and not fail_fast:
                # We have errors to raise which have not already been raised.
                exc = errors[0]
                raise_exc(
                    exc=exc.error,
                    on_error=on_error,
                    errors=errors,
                    fail_fast=fail_fast,
                    force=True,
                )

            # Call the wrapped function:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def analyse_sig(*parse_args, **parse_kwargs):
    """
    Decorator for methods (to analyse) the args and kwargs of the decorated callable.
    This method does not modify the args or kwargs in any way.

    :param parse_args: A list of callables which accept two values only:
    These callables will be passed the target function's argument at the same position as - the
    callable is in the decorator's arguments list and the index of the argument.
    If callable==IGNORE, then the decorated function's arg is not parsed.
    :param parse_kwargs: A dictionary of name, callables. The name represents the target
    function's kwarg that will be passed to the callable. The callable receives the name,
    value and a boolean representing if the name is present in the kwargs:
    ie: `def my_func(name, value, name_in_decorated_funcs_passed_kwargs)`.
    :param bool parse_kwargs['_fail_fast_']: True: Fail on the first exception raised by any
    supplied callable.
    :param bool parse_kwargs['_on_error_']: Callable or type to be called when an exception is found
    in a supplied callable, if the type is an exception or subclass-of, it will be raised (the
    exception constructor should take the same signature as my_func below):
    ie: `def my_func(exc, list_of_excs)`.
    If the type is not an exception or subclass-of it will be called, it is up to this callable to
    raise an exception if required.
    :param bool parse_kwargs['_strict_']: True=Error if all params are not analysed.
    :param callable parse_kwargs['_default_']: Default handler for all not previously analysed
    arguments.
    :returns: Decorated function.
    :note: Any exception raised by a supplied callable will have an additional field: `_errors_`.
    This is always a list of one or all of the errors encountered during the supplied callables (
    depending on the value of the `_fail_fast_` kwargs.

    Example:
    @hoft.analyse_in(
        _a_func(z=1), None, bar=_b_func(x=1, y=2), baz=_validate_baz(), x=None,
        _fail_fast_=True, _on_error_=my_func, _strict_=False, _default_=_default_func,
    )
    def _validate_something_decorated(foo, ignored, bar=hoft.IGNORE, baz=None, x=None):
        ...

    """
    def decorator(func):
        @six.wraps(func)
        def wrapper(*args, **kwargs):
            argspec = getargspec(func)
            callargs = getcallargs(func, *args, **kwargs)

            strict = parse_kwargs.pop('_strict_', None)
            default = parse_kwargs.pop('_default_', None)
            fail_fast = parse_kwargs.pop('_fail_fast_', False)
            on_error = parse_kwargs.pop('_on_error_', None)

            errors = parse_all_sig_args(
                parse_args,
                parse_kwargs,
                args,
                kwargs,
                argspec,
                callargs,
                strict,
                default,
                on_error,
                fail_fast,
            )

            if errors and not fail_fast:
                # We have errors to raise which have not already been raised.
                exc = errors[0]
                raise_exc(
                    exc=exc.error,
                    on_error=on_error,
                    errors=errors,
                    fail_fast=fail_fast,
                    force=True,
                )

            # Call the wrapped function:
            return func(*args, **kwargs)

        return wrapper

    return decorator
