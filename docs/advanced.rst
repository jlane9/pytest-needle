=================
Advanced Settings
=================

-------
Engines
-------

By default Needle uses the PIL engine (``needle.engines.pil_engine.Engine``) to take screenshots. Instead of PIL, you may also use PerceptualDiff or ImageMagick.


Example with PerceptualDiff:

.. code-block:: bash

    pytest --driver Chrome --needle-engine perceptualdiff test_example.py

Example with ImageMagick:

.. code-block:: bash

    pytest --driver Chrome --needle-engine imagemagick test_example.py

Besides being much faster than PIL, PerceptualDiff and ImageMagick also generate a diff PNG file when a test fails, highlighting the differences between the baseline image and the new screenshot.

Note that to use the PerceptualDiff engine you will first need to `download <http://pdiff.sourceforge.net/>`_ the perceptualdiff binary and place it in your PATH.

To use the ImageMagick engine you will need to install a package on your machine (e.g. sudo apt-get install imagemagick on Ubuntu or brew install imagemagick on OSX).


------------
File cleanup
------------

Each time you run tests, Needle will create new screenshot images on disk, for comparison with the baseline screenshots.
It’s then up to you whether you want to delete them or archive them. To remove screenshots from successful test use:

.. code-block:: bash

    pytest --driver Chrome --needle-cleanup-on-success test_example.py

Any unsuccessful tests will remain on the file system.


-----------
File output
-----------

To specify a path for baseline image path use:

.. code-block:: bash

    pytest --driver Chrome --needle-baseline-dir /path/to/baseline/images

Default path is ./screenshots/baseline

To specify a path for output image path use:

.. code-block:: bash

    pytest --driver Chrome --needle-output-dir /path/to/output/images

Default path is ./screenshots


-----------------------
Generating HTML reports
-----------------------

To generate html reports use:

.. code-block:: bash

    pytest --driver Chrome --html=report.html --self-contained-html