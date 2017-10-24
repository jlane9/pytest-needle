"""test_example

.. codeauthor:: John Lane <jlane@fanthreesixty.com>

"""

import pytest
from selenium.webdriver.common.by import By


@pytest.mark.page
def test_example_page(needle):
    """Example for comparing entire pages

    :param NeedleDriver needle: NeedleDriver instance
    :return:
    """

    # Navigate to web page
    needle.driver.get('https://www.example.com')

    # Take a entire page screen diff
    needle.assert_screenshot('static_page', threshold=10)


@pytest.mark.mask
def test_example_page_with_mask(needle):
    """Example for comparing page with a mask

    :param NeedleDriver needle: NeedleDriver instance
    :return:
    """

    # Navigate to web page
    needle.driver.get('https://www.google.com')

    # Ensure the cursor does not appear in the screenshot
    footer = needle.driver.find_elements_by_xpath('//div[@class="fbar"]')

    if footer:
        footer[0].click()

    # Take a entire page screen diff, ignore the doodle banner
    needle.assert_screenshot('search_page', exclude=[(By.ID, 'hplogo'), (By.ID, 'prm')], threshold=80)


@pytest.mark.element
def test_example_element(needle):
    """Example for comparing individual elements

    :param NeedleDriver needle: NeedleDriver instance
    :return:
    """

    # Navigate to web page
    needle.driver.get('https://www.google.com')

    # Ensure the cursor does not appear in the screenshot
    footer = needle.driver.find_elements_by_xpath('//div[@class="fbar"]')

    if footer:
        footer[0].click()

    # Take an element screen diff
    needle.assert_screenshot('search_field', (By.ID, 'tsf'), threshold=80)
