.. pytest-needle documentation master file, created by
   sphinx-quickstart on Wed Oct 25 11:30:00 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============
pytest-needle
=============

.. image:: https://travis-ci.org/jlane9/pytest-needle.svg?branch=master
    :target: https://travis-ci.org/jlane9/pytest-needle

.. image:: https://coveralls.io/repos/github/jlane9/pytest-needle/badge.svg?branch=master
    :target: https://coveralls.io/github/jlane9/pytest-needle?branch=master

.. image:: https://landscape.io/github/jlane9/pytest-needle/master/landscape.svg?style=flat
    :target: https://landscape.io/github/jlane9/pytest-needle/master

.. image:: https://badge.fury.io/py/pytest-needle.svg
    :target: https://badge.fury.io/py/pytest-needle

.. image:: https://img.shields.io/pypi/pyversions/pytest-needle.svg
    :target: https://pypi.python.org/pypi/pytest-needle

.. image:: https://img.shields.io/pypi/l/pytest-needle.svg
    :target: https://pypi.python.org/pypi/pytest-needle

.. image:: https://img.shields.io/pypi/status/pytest-needle.svg
    :target: https://pypi.python.org/pypi/pytest-needle

.. image:: https://requires.io/github/jlane9/pytest-needle/requirements.svg?branch=master
    :target: https://requires.io/github/jlane9/pytest-needle/requirements/?branch=master

.. image:: https://readthedocs.org/projects/pytest-needle/badge/?version=latest
    :target: http://pytest-needle.readthedocs.io/en/latest/?badge=latest

pytest-needle is a pytest implementation of `needle <https://github.com/python-needle/needle>`_.

It's fairly similar to needle and shares much of the same functionality,
except it uses `pytest-selenium <https://github.com/pytest-dev/pytest-selenium>`_ for handling the webdriver
and implements needle as a fixture instead of having test cases inherit from needle's base test class.


.. toctree::
   :maxdepth: 2

   Installation <install>
   Getting Started <readme>
   Advanced Settings <advanced>
   API Reference <pytest_needle>
   Development <development>
   Miscellaneous <misc>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
