#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# HOFT signatures.
# @module hoft.core.sigs
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

from inspect import getargspec

from hoft.core.utils import NoDefaultError, Signature

__all__ = [
    'num_keywords',
    'num_positionals',
    'get_keywords',
    'get_positionals',
    'get_default_value',
    'get_signature',
    'signature',
]


def num_keywords(argspec):
    """
    Determine the number of keyword arguments (eg: `def func(name=value)`).

    :param inspect.ArgSpec argspec:
        A previously obtained argspec.
    :return:
        Number of positional arguments.
    :rtype: int
    """
    return len(argspec.defaults or [])


def num_positionals(argspec, num_keyword_args=None):
    """
    Determine the number of positional arguments (eg: `def func(name)`).

    :param inspect.ArgSpec argspec:
        A previously obtained argspec.
    :param int num_keyword_args:
        Number of keyword arguments already known (if any, if not then they will be calculated).
    :return:
        Number of positional arguments.
    :rtype: int
    """
    return len(argspec.args) - num_keyword_args if num_keyword_args is not None else num_keywords(
        argspec)


def get_positionals(argspec, num_positional_args=None):
    """
    Get all positional arguments.

    :param inspect.ArgSpec argspec:
        A previously obtained argspec.
    :param int num_positional_args:
        Number of positional arguments already known (if any, if not then they will be calculated).
    :return:
        A list containing the positional arguments in declaration order.
    :rtype:
        List[str]
    """
    num_positional_args = num_positional_args if num_positional_args is not None else \
        num_positionals(argspec)

    return argspec.args[:num_positional_args]


def get_keywords(argspec, num_positional_args=None):
    """
    Get all keyword arguments and their associated default values.

    :param inspect.ArgSpec argspec:
        A previously obtained argspec.
    :param int num_positional_args:
        Number of positional arguments already known (if any, if not then they will be calculated).
    :return:
        A dictionary containing the keyword names and their associated default values.
    :rtype:
        Dict[str, int]
    """
    num_positional_args = num_positional_args if num_positional_args is not None else \
        num_positionals(argspec)

    return {
        name: default_value
        for name, default_value in zip(argspec.args[num_positional_args:], argspec.defaults or [])
    }


def get_default_value(name, argspec):
    """
    Get the default value for the keyword argument of name.

    :param str name:
        The name to get the default keyword argument value for.
    :param inspect.ArgSpec argspec:
        A previously obtained argspec.
    :return:
        The default_value present in the method's signature.
    :raises:
        NoDefaultError When no default value can or does exist fo the name.
    """
    try:
        default_index = argspec.args.index(name) - len(argspec.args)
    except ValueError:
        raise NoDefaultError(name, argspec)

    try:
        return argspec.defaults[default_index]
    except (IndexError, TypeError):
        raise NoDefaultError(name, argspec)


def get_signature(argspec):
    """
    Obtain a Signature from an argspec

    :param inspect.ArgSpec argspec:
        A previously obtained argspec.
    :return:
        The signature.
    :rtype:
        Signature
    """
    num_keyword_args = num_keywords(argspec)
    num_positional_args = num_positionals(argspec, num_keyword_args=num_keyword_args)
    positionals = get_positionals(argspec, num_positional_args=num_positional_args)
    keywords = get_keywords(argspec, num_positional_args=num_positional_args)

    return Signature(positionals, argspec.varargs, keywords, argspec.keywords or None)


def signature(func):
    """
    Obtain a method's Signature.

    :param callable func:
        Method to obtain the signature for.
    :return:
        The method's signature.
    :rtype:
        Signature
    """
    return get_signature(getargspec(func))
