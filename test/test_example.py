"""test_example

.. codeauthor:: John Lane <jlane@fanthreesixty.com>

"""

import pytest


@pytest.mark.page
def test_example_page(needle):
    """Example for comparing entire pages

    :param NeedleDriver needle: NeedleDriver instance
    :return:
    """

    # Navigate to web page
    needle.driver.get('https://www.google.com')

    # Take a entire page screen diff
    needle.assert_screenshot('search_page')
