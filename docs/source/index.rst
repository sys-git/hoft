.. hoft documentation master file, created by
   sphinx-quickstart on Fri Aug 11 10:54:13 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

HOFT - Higher Order Func Tools for Python2.7
============================================

.. image:: https://coveralls.io/repos/github/sys-git/hoft/badge.svg
    :target: https://coveralls.io/github/sys-git/hoft
.. image:: https://readthedocs.org/projects/hoft/badge/?version=latest
    :target: http://hoft.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
Initially developed for parameter validation but now generic.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Currently a single decorator that can be used to programmatically analyse a function's input
positional and keyword arguments.

The params are then passed directly to the decorated function and any exceptions are propagated
back to the caller.

Simple example
--------------

.. code-block:: python

    from hoft import analyse_in, IGNORE

    def func_a(value, index):
        # do my thing and potentially raise an exception here
        ...
        raise MyError(value)

    ...

    @analyse_in(func_a, func_b, c=IGNORE, d=func_c)
    def my_function(a, b, c=None, d=None):
        ...

To install
----------

.. code-block:: bash

    $ pip install hoft

Contributions
-------------
Fork me and create a pull request! All contributions or suggestions welcome :)

Indices, tables and examples
============================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`examples`
* :ref:`search`
