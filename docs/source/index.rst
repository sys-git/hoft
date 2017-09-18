.. hoft

HOFT - Higher Order Func Tools for Python2.7
============================================

.. image:: https://img.shields.io/badge/Author:%20francis%20horsman-Available-brightgreen.svg?style=plastic
    :target: https://www.linkedin.com/in/francishorsman
.. image:: https://travis-ci.org/sys-git/hoft.svg?branch=master
    :target: https://travis-ci.org/sys-git/hoft
.. image:: https://coveralls.io/repos/github/sys-git/hoft/badge.svg
    :target: https://coveralls.io/github/sys-git/hoft
.. image:: https://readthedocs.org/projects/hoft/badge/?version=latest
    :target: http://hoft.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://badge.fury.io/py/hoft.svg
    :target: https://badge.fury.io/py/hoft
.. image:: https://img.shields.io/pypi/l/hoft.svg
    :target: https://img.shields.io/pypi/l/hoft.svg
.. image:: https://img.shields.io/pypi/wheel/hoft.svg
    :target: https://img.shields.io/pypi/wheel/hoft.svg
.. image:: https://img.shields.io/pypi/pyversions/hoft.svg
    :target: https://img.shields.io/pypi/pyversions/hoft.svg
.. image:: https://img.shields.io/pypi/status/hoft.svg
    :target: https://img.shields.io/pypi/status/hoft.svg

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Decorators that can be used to analyse a function's positional, keyword and default arguments.

HOFT uses **getargspec** and **getcallargs** (from the `inspect <https://docs.python.org/2/library/inspect.html>`_ module) under the hood.

The params are then passed directly to the decorated function and any exceptions are propagated back to the caller.

Use case
--------

1. Used in conjunction with a parameter checking and validation library to perform parameter validation prior to function execution.

.. code-block:: python

    from hoft import analyse_sig, IGNORE
    from certifiable import certify_int, certify_string
    ...

    @analyse_sig(certify_int(min_value=-100, max_value=100), IGNORE, c=IGNORE, d=certify_string(max_length=2))
    def my_function(a, b, c=None, d=None, e='world'):
        ...

    >>> my_function(-256, 'x', 'y', 'abcd')
    Traceback (most recent call last):
    ...
    CertifierError: .....

Simple example
--------------

.. code-block:: python

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

Helpful utilities
-----------------

:ref:`sigs` contains functions to extract a useful signature and signature components from an argspec.

To install
----------

.. code-block:: bash

    $ pip install hoft

Contributions
-------------
Fork me and create a pull request!

All contributions or suggestions welcome :)

Coding guidelines in the next version.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
