<h1>H.O.F.T</h1>

[![Author](https://img.shields.io/badge/Author:%20francis%20horsman-Available-brightgreen.svg?style=plastic)](https://www.linkedin.com/in/francishorsman)

<h2>Higher Order Func Tools for Python2.7</h2>

[![Build Status](https://travis-ci.org/sys-git/hoft.svg?branch=master)](https://travis-ci.org/sys-git/hoft)
[![Coverage Status](https://coveralls.io/repos/github/sys-git/hoft/badge.svg)](https://coveralls.io/github/sys-git/hoft)
[![Documentation Status](https://readthedocs.org/projects/hoft/badge/?version=latest)](http://hoft.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/hoft.svg)](https://badge.fury.io/py/hoft)
[![PyPI](https://img.shields.io/pypi/l/hoft.svg)]()
[![PyPI](https://img.shields.io/pypi/wheel/hoft.svg)]()
[![PyPI](https://img.shields.io/pypi/pyversions/hoft.svg)]()
[![PyPI](https://img.shields.io/pypi/status/hoft.svg)]()

Decorators that can be used to analyse a function's positional, keyword and default arguments.

HOFT uses **getargspec** and **getcallargs** (from the <a href="https://docs.python.org/2/library/inspect.html">inspect</a>
module) under the hood.

The params are then passed directly to the decorated function and any exceptions are propagated back to the caller.

<h3>Read documentation</h3>
Complete documentation can be found at <a href="http://hoft.readthedocs.io/en/latest/">readthedocs</a>

<h3>Use case</h3>

1. Used in conjunction with a parameter checking and validation library to perform parameter validation prior to function execution.

```
    from hoft import analyse_sig, IGNORE
    from validation_lib import validate_int, validate_string
    ...

    @analyse_sig(validate_int(min_value=-100, max_value=100), IGNORE, c=IGNORE, d=validate_string(max_length=2))
    def my_function(a, b, c=None, d=None, e='world'):
        ...

    >>> my_function(-256, 'x', 'y', 'abcd')
    Traceback (most recent call last):
    ...
    validation_lib_error: .....
```

<h3>Simple example</h3>

```
    from hoft import analyse_sig, IGNORE
    
    def func(arg_name, arg_index, arg_value, default_value=None):
        # do my thing and potentially raise an exception here
        if arg_name == 'a':
            assert arg_index==0
            assert arg_value==5
        elif arg_name == 'd':
            assert arg_index==2
            assert called_with_value==7
            assert default_value==None

        ...
        raise MyError(value)

    ...


    @analyse_sig(func, IGNORE, c=IGNORE, d=func)
    def my_function(a, b, c=None, d=None, e='world'):
        ...


    # call the decorated method, and the arguments will be checked prior to my_function execution:
    my_function(5, 6, c=7, d=8)

    # my_function is called as expected and receives: a=5, b=6, c=7, d=8, e='world'
```

<h3>To install</h3>

```
    $ pip install hoft
```

<h3>Build documentation</h3>

```
    $ make sphinx-html
```
