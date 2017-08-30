#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Argument parsers.
# @module hoft.core.parsers
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

from hoft.core.sigs import get_default_value
from hoft.core.utils import (
    IGNORE, KeywordError, PositionalError, conditionally_raise_exc, get_func_name,
)


def parse_positional_inputs(parse_args, args, argspec, errors, on_error, fail_fast):
    # Parse the positional inputs:
    for index, (custom_parser_func, value) in enumerate(zip(parse_args, args)):
        # Only (validate) if the func is provided:
        if custom_parser_func is not IGNORE:
            try:
                custom_parser_func(
                    value=value,
                    index=index,
                )
            except Exception as exc:
                func_name = get_func_name(custom_parser_func)
                name = argspec.args[index]
                errors.append(
                    PositionalError(
                        exc,
                        name,
                        index,
                        value,
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


def parse_keyword_inputs(parse_kwargs, kwargs, argspec, errors, on_error, fail_fast):
    # Parse the keyword inputs we name:
    for name, custom_parser_func in parse_kwargs.items():
        # Only (validate) if the func is provided:
        if custom_parser_func is not IGNORE:
            value = kwargs.get(name)
            try:
                custom_parser_func(
                    value=value,
                    name=name,
                    present=name in kwargs,
                )
            except Exception as exc:
                func_name = get_func_name(custom_parser_func)
                default_value = get_default_value(name, argspec)
                errors.append(
                    KeywordError(
                        exc,
                        name,
                        value,
                        default_value,
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


def parse_all_in_args(
    parse_args, parse_kwargs, args, kwargs, argspec, on_error, fail_fast,
):
    errors = []

    parse_positional_inputs(
        parse_args,
        args,
        argspec,
        errors,
        on_error,
        fail_fast,
    )

    parse_keyword_inputs(
        parse_kwargs,
        kwargs,
        argspec,
        errors,
        on_error,
        fail_fast,
    )

    return errors
