#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Argument parsers.
# @module hoft.core.parsers
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

from hoft.core.sigs import get_default_value, get_signature
from hoft.core.utils import (
    ArgsNotAnalysedError, IGNORE, KeywordError, NOVALUE, NotAnalysedError, PositionalError,
    conditionally_raise_exc, get_func_name,
)


def parse_sig_positional_inputs(
    parse_args, args, argspec, errors, handled, on_error, fail_fast,
):
    # Parse the positional inputs:
    for index, (custom_parser_func, value) in enumerate(zip(parse_args, args)):
        # Only (validate) if the func is provided:
        if custom_parser_func is not IGNORE:
            name = argspec.args[index]

            # Have we already handled this argument?
            if name in handled:
                continue

            handled.update([name])

            try:
                custom_parser_func(
                    name,
                    index,
                    value,
                )
            except Exception as exc:
                func_name = get_func_name(custom_parser_func)
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


def parse_sig_keyword_inputs(
    parse_kwargs, kwargs, argspec, callargs, errors, handled, on_error, fail_fast,
):
    for name, custom_parser_func in sorted(parse_kwargs.items()):
        if name in handled:
            continue
        handled.update([name])

        # Only (validate) if the func is provided:
        if custom_parser_func is not IGNORE:
            called_with_value = kwargs.get(name, NOVALUE)
            default_value = get_default_value(name, argspec)
            index = argspec.args.index(name)

            try:
                custom_parser_func(
                    name,
                    index,
                    called_with_value,
                    default_value=default_value,
                )
            except Exception as exc:
                func_name = get_func_name(custom_parser_func)
                errors.append(
                    KeywordError(
                        exc,
                        name,
                        called_with_value,
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


def parse_sig_remaining_inputs(
    default, argspec, callargs, kwargs, errors, handled, on_error, fail_fast,
):
    sig = get_signature(argspec)

    for name, value in sorted(callargs.items()):
        if name in handled:
            continue
        handled.update([name])

        # Only (validate) if the func is provided:
        if default is not IGNORE:
            try:
                default(name, value, argspec)
            except Exception as exc:
                func_name = get_func_name(default)
                default_value = callargs[name]
                try:
                    index = sig.args.index(name)
                except ValueError:
                    errors.append(
                        KeywordError(
                            exc,
                            name,
                            value,
                            default_value,
                            func_name,
                            default,
                        )
                    )
                else:
                    errors.append(
                        PositionalError(
                            exc,
                            name,
                            index,
                            value,
                            func_name,
                            default,
                        )
                    )

                conditionally_raise_exc(
                    exc=exc,
                    on_error=on_error,
                    errors=errors,
                    fail_fast=fail_fast,
                )


def parse_all_sig_args(
    parse_args, parse_kwargs, args, kwargs, argspec, callargs, strict, default, on_error, fail_fast,
):
    errors = []
    handled = set()

    parse_sig_positional_inputs(
        parse_args,
        args,
        argspec,
        errors,
        handled,
        on_error,
        fail_fast,
    )

    parse_sig_keyword_inputs(
        parse_kwargs,
        kwargs,
        argspec,
        callargs,
        errors,
        handled,
        on_error,
        fail_fast,
    )

    arg_names = set(callargs.keys())

    if default:
        parse_sig_remaining_inputs(
            default,
            argspec,
            callargs,
            kwargs,
            errors,
            handled,
            on_error,
            fail_fast,
        )

    if strict:
        names = sorted(list(arg_names - handled))

        if names:
            try:
                raise ArgsNotAnalysedError(names)
            except ArgsNotAnalysedError as exc:
                errors.append(NotAnalysedError(exc, names, argspec, callargs))
                conditionally_raise_exc(
                    exc=exc,
                    on_error=on_error,
                    errors=errors,
                )

    return errors
