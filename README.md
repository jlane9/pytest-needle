pytest-needle
=============
[![Build Status](https://travis-ci.org/jlane9/pytest-needle.svg?branch=master)](https://travis-ci.org/jlane9/pytest-needle)
[![Coverage Status](https://coveralls.io/repos/github/jlane9/pytest-needle/badge.svg?branch=master)](https://coveralls.io/github/jlane9/pytest-needle?branch=master)

pytest-needle is a pytest implementation of [needle](https://github.com/python-needle/needle).

It's fairly similar to needle and shares much of the same functionality, 
except it uses [pytest-selenium](https://github.com/pytest-dev/pytest-selenium) for handling the webdriver 
and implements needle as a fixture instead of having test cases inherit from needle's base test class.


Installation
------------

Install through pip:

```bash
pip install pytest-needle
```


Install from source:

```bash

cd /path/to/source/pytest-needle
python setup.py install 
```

Example
-------

Example needle pytest implementation:

```python
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

```

To create a baseline for all subsequent test run:

```bash
pytest --driver Chrome --needle-save-baseline test_example.py
```

After we have a baseline, to run test use:

```bash
pytest --driver Chrome test_example.py
```

Selecting a WebDriver
---------------------

To control which browser to use, use `--driver <BROWSER>` from pytest-selenium. For example to change to browser to Firefox:

```bash
pytest --driver Firefox test_example.py
```

Setting the viewport's size
---------------------------

You may set the size of the browser's viewport using the `set_viewport_size()` on the needle fixture

```python

def test_example_viewport(needle):

    # Navigate to web page
    needle.set_viewport_size(width=1024, height=768)
    
    # Rest of the test ...
    
```

You may also set the default viewport size for all your tests by using the command line argument `--needle-viewport-size`:

```bash
pytest --driver Chrome --needle-viewport-size "1024 x 768" test_example.py
```

Excluding areas
---------------

Sometimes areas on a web page may contain dynamic content and cause false negatives, or worse convince testers to raise 
the threshold at which changes are acceptable. You can instead choose to mask these areas to avoid the issue of consistently
failing tests:

```python
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
```

In the case with Google's home page the doodle banner frequently changes, so to visually regress day-to-day requires 
generating new baselines every time the banner is updated. Masking allows only the banner to be ignored while the rest 
of the page can be evaluated.


Engines
-------

By default Needle uses the PIL engine (`needle.engines.pil_engine.Engine`) to take screenshots. Instead of PIL, you may also use PerceptualDiff or ImageMagick.


Example with PerceptualDiff:

```bash
pytest --driver Chrome --needle-engine perceptualdiff test_example.py
```
 
Example with ImageMagick:
 
```bash
pytest --driver Chrome --needle-engine imagemagick test_example.py
```
 
Besides being much faster than PIL, PerceptualDiff and ImageMagick also generate a diff PNG file when a test fails, highlighting the differences between the baseline image and the new screenshot.

Note that to use the PerceptualDiff engine you will first need to [download](http://pdiff.sourceforge.net/) the perceptualdiff binary and place it in your PATH.

To use the ImageMagick engine you will need to install a package on your machine (e.g. sudo apt-get install imagemagick on Ubuntu or brew install imagemagick on OSX).


File cleanup
------------

Each time you run tests, Needle will create new screenshot images on disk, for comparison with the baseline screenshots. 
It’s then up to you whether you want to delete them or archive them. To remove screenshots from successful test use:

```bash
pytest --driver Chrome --needle-cleanup-on-success test_example.py
```

Any unsuccessful tests will remain on the file system.


File output
-----------

To specify a path for baseline image path use:

```bash
pytest --driver Chrome --needle-baseline-dir /path/to/baseline/images
```

Default path is ./screenshots/baseline

To specify a path for output image path use:

```bash
pytest --driver Chrome --needle-output-dir /path/to/output/images
```

Default path is ./screenshots


Generating HTML reports
-----------------------

To generate html reports use:

```bash
pytest --driver Chrome --html=report.html --self-contained-html
```
