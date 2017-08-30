#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# HOFT utils.
# @module hoft.core.utils
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

from collections import namedtuple

PositionalError = namedtuple('PositionalError', (
    'error', 'name', 'index', 'value', 'func_name', 'func')
)

KeywordError = namedtuple('KeywordError', (
    'error', 'name', 'value', 'default_value', 'func_name', 'func')
)

NotAnalysedError = namedtuple('NotAnalysedError', (
    'error', 'name', 'argspec', 'callargs')
)

Signature = namedtuple(
    'Signature', ('args', 'vaargs', 'kwargs', 'keywords')
)
"""
A Signature representing a parsed argspec for a function:

:param list args: The positional argument names.
:param Union[string|None] vaargs: The positional varargs name (eg after a `*`).
:param dict kwargs: The keyword argument names and associated default values.
:param Union[string|None] keywords: The keyword varkwargs name (eg: after a `**`).

**Example**:
    def func(a, b, c=1, \**d) === Signature(['a', 'b'], None, {'c': 1}, 'd')

"""

IGNORE = None
"""
Use this to tell hoft to ignore a function argument when analysing it.
"""

NOVALUE = object()
"""
A special value to indicate that no value was passed to the function for a keyword argument.
"""

__all__ = [
    'IGNORE',
    'NOVALUE',
    'ArgsNotAnalysedError',
    'NoDefaultError',
]


class ArgsNotAnalysedError(Exception):
    """
    One or more arguments were not analysed (when `strict=True`).
    """

    def __init__(self, names):
        """
        :param List[str] names:
            Arguments not analysed (in declared order).
        """
        super(ArgsNotAnalysedError, self).__init__(
            'ArgsNotAnalysedError: {names}'.format(names=names)
        )
        self.names = names


class NoDefaultError(Exception):
    """
    No default value is provided for this argument.
    """

    def __init__(self, name, argspec):
        """

        :param str name:
            Name of the argument
        :param inspect.ArgSpec argspec:
            Existing argspec.
        """
        super(NoDefaultError, self).__init__(
            'no default value for positional: {k}'.format(k=name))
        self.name = name
        self.argspec = argspec


def get_func_name(func):
    try:
        return func.func_name
    except Exception:  # NOQA
        # Unable to determine target function validator:
        return None


def raise_exc(exc, on_error=None, errors=None, fail_fast=False, force=False):
    if fail_fast or force:
        if on_error is not None:
            if isinstance(on_error, Exception):
                # Raise the custom exception if required:
                raise on_error(exc, errors)
            elif callable(on_error):
                # Call the user-defined function as required, it is up to it to raise an exception.
                on_error(exc, errors)
        else:
            # Add the errors to the exception and raise it:
            exc._errors_ = errors
            raise exc


def conditionally_raise_exc(exc, on_error=None, errors=None, fail_fast=False):
    raise_exc(
        exc=exc,
        on_error=on_error,
        errors=errors,
        fail_fast=fail_fast,
        force=False,
    )
