===========
Development
===========

------------
Installation
------------

To install for development, simply run the following commands:

.. code-block:: bash

    git clone https://github.com/jlane9/pytest-needle
    cd pyest-needle
    pip install -r requirements.txt
    pip install -e .

------------------------
Generating documentation
------------------------

You can either use makefile:

.. code-block:: bash

    cd docs
    make html

Or you can use autobuild:

.. code-block:: bash

    cd docs
    sphinx-autobuild . _build/html/

-------------
Running Tests
-------------

To run tests you must first provide a base line to go against:

.. code-block:: bash

    pytest --driver Chrome --needle-save-baseline test/

Then all runs afterwards can be just:

.. code-block:: bash

    pytest --driver Chrome --pep8 pytest_needle --cov pytest_needle --cov-report term-missing test/