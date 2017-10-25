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
