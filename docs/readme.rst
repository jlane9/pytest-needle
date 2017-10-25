=============
pytest-needle
=============

-------
Example
-------

Example needle pytest implementation:


.. code-block:: python

    """test_example.py
    """

    from selenium.webdriver.common.by import By
    import pytest

    @pytest.mark.element
    def test_example_element(needle):
        """Example for comparing individual elements

        :param NeedleDriver needle: NeedleDriver instance
        :return:
        """

        # Navigate to web page
        needle.driver.get('https://www.google.com')

        # Take an element screen diff
        needle.assert_screenshot('search_field', (By.ID, 'tsf'))

To create a baseline for all subsequent test run:

.. code-block:: bash

    pytest --driver Chrome --needle-save-baseline test_example.py

After we have a baseline, to run test use:

.. code-block:: bash

    pytest --driver Chrome test_example.py

---------------------
Selecting a WebDriver
---------------------

To control which browser to use, use ``--driver <BROWSER>`` from pytest-selenium. For example to change to browser to Firefox:

.. code-block:: bash

    pytest --driver Firefox test_example.py

---------------------------
Setting the viewport's size
---------------------------

You may set the size of the browser's viewport using the ``set_viewport_size()`` on the needle fixture

.. code-block:: python

    def test_example_viewport(needle):

        # Navigate to web page
        needle.set_viewport_size(width=1024, height=768)

        # Rest of the test ...

You may also set the default viewport size for all your tests by using the command line argument ``--needle-viewport-size``:

.. code-block:: bash

    pytest --driver Chrome --needle-viewport-size "1024 x 768" test_example.py

---------------
Excluding areas
---------------

Sometimes areas on a web page may contain dynamic content and cause false negatives, or worse convince testers to raise
the threshold at which changes are acceptable. You can instead choose to mask these areas to avoid the issue of consistently
failing tests:

.. code-block:: python

    """test_example.py
    """

    from selenium.webdriver.common.by import By
    import pytest


    @pytest.mark.mask
    def test_example_page_with_mask(needle):
        """Example for comparing page with a mask

        :param NeedleDriver needle: NeedleDriver instance
        :return:
        """

        # Navigate to web page
        needle.driver.get('https://www.google.com')

        # Take a entire page screen diff, ignore the doodle banner
        needle.assert_screenshot('search_page', threshold=60, exclude=[(By.ID, 'hplogo'), (By.ID, 'prm')])

In the case with Google's home page the doodle banner frequently changes, so to visually regress day-to-day requires
generating new baselines every time the banner is updated. Masking allows only the banner to be ignored while the rest
of the page can be evaluated.