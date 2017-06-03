"""pytest_needle.plugin

.. codeauthor:: John Lane <jlane@fanthreesixty.com>

"""

from __future__ import absolute_import
import base64
import os
import pytest
from pytest_needle.driver import DEFAULT_BASELINE_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_ENGINE, \
    DEFAULT_VIEWPORT_SIZE, NeedleDriver
from pytest_needle.exceptions import ImageMismatchException


def pytest_addoption(parser):
    """

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

    group.addoption('--needle-baseline-dir', action='store', dest='baseline_dir',
                    metavar='dir', default=DEFAULT_BASELINE_DIR,
                    help='where to store baseline images')

    group.addoption('--needle-output-dir', action='store', dest='output_dir',
                    metavar='dir', default=DEFAULT_OUTPUT_DIR,
                    help='where to store baseline images')

    group.addoption('--needle-viewport-size', action='store', dest='viewport_size',
                    metavar='pixels', default=DEFAULT_VIEWPORT_SIZE,
                    help='size of window width (px) x height (px)')


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

    if is_failure(report) and call.excinfo:

        exception = call.excinfo.value

        if isinstance(exception, ImageMismatchException):

            pytest_html = item.config.pluginmanager.getplugin('html')

            if pytest_html is not None:

                if os.path.exists(exception.baseline_image):

                    report.extra.append(pytest_html.extras.image(
                        get_image_as_base64(exception.baseline_image),
                        'PDIFF: Expected'
                    ))

                diff_path = exception.output_image.replace('.png', '.diff.png')

                if os.path.exists(diff_path):
                    report.extra.append(pytest_html.extras.image(
                        get_image_as_base64(diff_path),
                        'PDIFF: Comparison'
                    ))

                if os.path.exists(exception.output_image):

                    report.extra.append(pytest_html.extras.image(
                        get_image_as_base64(exception.output_image),
                        'PDIFF: Actual'
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

    options = {
        'cleanup_on_success': request.config.getoption('needle_cleanup_on_success'),
        'save_baseline': request.config.getoption('needle_save_baseline'),
        'needle_engine': request.config.getoption('needle_engine'),
        'baseline_dir': request.config.getoption('baseline_dir'),
        'output_dir': request.config.getoption('output_dir'),
        'viewport_size': request.config.getoption('viewport_size')
    }

    return NeedleDriver(selenium, **options)
