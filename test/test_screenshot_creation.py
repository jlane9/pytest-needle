#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_example

.. codeauthor:: Kevin Möellering

"""

import os


def test_screenshot(needle):

    SCREENSHOT_NAME = 'screenshot_without_baseline'
    needle.driver.get('https://www.example.com')
    screenshot_dir = os.path.join(needle.output_dir, needle.build) if needle.categorize else needle.output_dir
    screenshot_path = os.path.join(screenshot_dir, SCREENSHOT_NAME + ".png")

    try:
        needle.assert_screenshot(SCREENSHOT_NAME)
    except IOError:
        pass

    assert os.path.isfile(screenshot_path), "Fresh screenshot was not created (there is no baseline image)"
