#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Argument parsers.
# @module hoft.core.parsers
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

from .utils import IGNORE, KeywordError, PositionalError, conditionally_raise_exc, get_func_name


def _parse_positional_inputs(parse_args, args, errors, on_error, fail_fast):
    # Parse the positional inputs:
    for index, (custom_parser_func, param) in enumerate(zip(parse_args, args)):
        # Only (validate) if the func is provided:
        if custom_parser_func is not IGNORE:
            try:
                custom_parser_func(param, index=index)
            except Exception as exc:
                func_name = get_func_name(custom_parser_func)
                errors.append(
                    PositionalError(
                        exc,
                        index,
                        param,
                        func_name,
                        custom_parser_func,
                    )
                )
                conditionally_raise_exc(
                    exc=exc,
                    on_error=on_error,
                    errors=errors,
                    fail_fast=fail_fast,
                )


def _parse_keyword_inputs(parse_kwargs, kwargs, errors, on_error, fail_fast):
    # Parse the keyword inputs we name:
    for name, custom_parser_func in parse_kwargs.items():
        # Only (validate) if the func is provided:
        if custom_parser_func is not IGNORE:
            param = kwargs.get(name)
            try:
                custom_parser_func(name, param, name in kwargs)
            except Exception as exc:
                func_name = get_func_name(custom_parser_func)
                errors.append(
                    KeywordError(
                        exc,
                        param,
                        func_name,
                        custom_parser_func,
                    )
                )
                conditionally_raise_exc(
                    exc=exc,
                    on_error=on_error,
                    errors=errors,
                    fail_fast=fail_fast,
                )
