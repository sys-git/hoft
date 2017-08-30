#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# HOFT utils.
# @module hoft.core.utils
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

from hoft.core.utils import NoDefaultError, Signature

__all__ = [
    'num_keywords',
    'num_positionals',
    'get_keywords',
    'get_positionals',
    'get_default_value',
    'get_sig',

]


def num_keywords(argspec):
    return len(argspec.defaults or [])


def num_positionals(argspec, num_keyword_args=None):
    return len(argspec.args) - num_keyword_args if num_keyword_args is not None else num_keywords(
        argspec)


def get_positionals(argspec, num_positional_args=None):
    num_positional_args = num_positional_args if num_positional_args is not None else \
        num_positionals(argspec)

    return argspec.args[:num_positional_args]


def get_keywords(argspec, num_positional_args=None):
    num_positional_args = num_positional_args if num_positional_args is not None else \
        num_positionals(argspec)

    return {
        name: default_value
        for name, default_value in zip(argspec.args[num_positional_args:], argspec.defaults or [])
    }


def get_default_value(name, argspec):
    try:
        default_index = argspec.args.index(name) - len(argspec.args)
    except ValueError:
        raise NoDefaultError(name, argspec)

    try:
        return argspec.defaults[default_index]
    except (IndexError, TypeError):
        raise NoDefaultError(name, argspec)


def get_signature(argspec):
    num_keyword_args = num_keywords(argspec)
    num_positional_args = num_positionals(argspec, num_keyword_args=num_keyword_args)
    positionals = get_positionals(argspec, num_positional_args=num_positional_args)
    keywords = get_keywords(argspec, num_positional_args=num_positional_args)

    return Signature(positionals, argspec.varargs, keywords, argspec.keywords or None)
