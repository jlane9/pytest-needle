#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pytest_needle.plugin

.. codeauthor:: John Lane <jlane@fanthreesixty.com>

"""

from __future__ import absolute_import
import base64
from datetime import datetime
import os
import pytest
from pytest_needle.driver import DEFAULT_BASELINE_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_ENGINE, \
    DEFAULT_VIEWPORT_SIZE, NeedleDriver
from pytest_needle.exceptions import ImageMismatchException


def pytest_addoption(parser):
    """Add command-line options to pytest runner

    :param parser:
    :return:
    """

    group = parser.getgroup('needle')
    group.addoption('--needle-cleanup-on-success', action='store_true',
                    help='destroy all non-baseline screenshots')

    group.addoption('--needle-save-baseline', action='store_true',
                    help='save baseline screenshots to disk')

    group.addoption('--needle-engine', action='store', dest='needle_engine', metavar='engine',
                    default=DEFAULT_ENGINE, help='engine for compare screenshots')

    group.addoption('--needle-baseline-dir', action='store', dest='needle_baseline_dir',
                    metavar='dir', default=DEFAULT_BASELINE_DIR,
                    help='where to store baseline images')

    group.addoption('--needle-output-dir', action='store', dest='needle_output_dir',
                    metavar='dir', default=DEFAULT_OUTPUT_DIR,
                    help='where to store baseline images')

    group.addoption('--needle-viewport-size', action='store', dest='needle_viewport_size',
                    metavar='pixels', default=DEFAULT_VIEWPORT_SIZE,
                    help='size of window width (px) x height (px)')

    group.addoption('--needle-build-name', action='store', dest='needle_build_name',
                    metavar='name', default=datetime.now().strftime('build_%Y.%m.%dT%H.%M.%S'),
                    help='specify name to give test run')


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """Add image diff to report

    :param item:
    :param call:
    :return:
    """

    outcome = yield
    report = outcome.get_result()
    report.extra = getattr(report, 'extra', [])

    # If the test passed, return
    if not (is_failure(report) and call.excinfo):
        return

    exception = call.excinfo.value

    # Only capture screenshots if they did not match
    if not isinstance(exception, ImageMismatchException):
        return

    pytest_html = item.config.pluginmanager.getplugin('html')

    # If pytest-html plugin is not available, return
    if pytest_html is None:
        return

    attachments = (
        (exception.baseline_image, 'PDIFF: Expected'),
        (exception.output_image.replace('.png', '.diff.png'), 'PDIFF: Comparison'),
        (exception.output_image, 'PDIFF: Actual')
    )

    for attachment in attachments:

        if os.path.exists(attachment[0]):

            report.extra.append(pytest_html.extras.image(
                get_image_as_base64(attachment[0]),
                attachment[1]
            ))


def is_failure(report):
    """True, if test failed

    :param report:
    :return:
    """

    xfail = hasattr(report, 'wasxfail')
    return (report.skipped and xfail) or (report.failed and not xfail)


def get_image_as_base64(filename):
    """Open image from file as base64 encoded string

    :param str filename: File path
    :return:
    """

    with open(filename, 'rb') as image:
        return base64.b64encode(image.read()).decode('ascii')


@pytest.fixture()
def needle(request, selenium):
    """Visual regression testing fixture

    :param request: pytest request
    :param selenium: Selenium web driver
    :return:
    """

    needle_args = ('needle_cleanup_on_success', 'needle_save_baseline', 'needle_engine', 'needle_baseline_dir',
                   'needle_output_dir', 'needle_viewport_size', 'needle_build_name')
    options = dict((key, request.config.getoption(key)) for key in needle_args)
    options['browser'] = request.config.getoption('driver')

    return NeedleDriver(selenium, **options)
