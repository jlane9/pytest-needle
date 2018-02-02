"""pytest_needle.driver

.. codeauthor:: John Lane <jlane@fanthreesixty.com>

"""

import base64
from errno import EEXIST
import math
import os
import re
import sys
import pytest
from needle.cases import import_from_string
from needle.engines.pil_engine import ImageDiff
from PIL import Image, ImageDraw, ImageColor
from selenium.webdriver.remote.webdriver import WebElement
from pytest_needle.exceptions import ImageMismatchException


if sys.version_info >= (3, 0):

    from io import BytesIO as IOClass

    # Ignoring since basetring is not redefined if running on python3
    # pylint: disable=W0622
    # pylint: disable=C0103
    basestring = str
    # pylint: enable=W0622
    # pylint: enable=C0103

else:
    try:
        from cStringIO import StringIO as IOClass
    except ImportError:
        from StringIO import StringIO as IOClass


DEFAULT_BASELINE_DIR = os.path.realpath(os.path.join(os.getcwd(), 'screenshots', 'baseline'))
DEFAULT_OUTPUT_DIR = os.path.realpath(os.path.join(os.getcwd(), 'screenshots'))
DEFAULT_ENGINE = 'needle.engines.pil_engine.Engine'
DEFAULT_VIEWPORT_SIZE = '1024x768'


class NeedleDriver(object):
    """NeedleDriver instance
    """

    ENGINES = {
        'pil': DEFAULT_ENGINE,
        'imagemagick': 'needle.engines.imagemagick_engine.Engine',
        'perceptualdiff': 'needle.engines.perceptualdiff_engine.Engine'
    }

    def __init__(self, driver, **kwargs):

        self.options = kwargs
        self.driver = driver

        # Create the output and baseline directories if they do not yet exist.
        for directory in (self.baseline_dir, self.output_dir):
            self._create_dir(directory)

        viewport_size = re.match(r'(?P<width>\d+)\s?[xX]\s?(?P<height>\d+)', self.viewport_size)

        # Set viewport position, size
        self.driver.set_window_position(0, 0)
        viewport_dimensions = (int(viewport_size.group('width')), int(viewport_size.group('height'))) if viewport_size \
            else (int(DEFAULT_VIEWPORT_SIZE.split('x')[0]), int(DEFAULT_VIEWPORT_SIZE.split('x')[1]))

        self.driver.set_window_size(*viewport_dimensions)

    @staticmethod
    def _create_dir(directory):
        """Recursively create a directory

        .. note:: From needle
            https://github.com/python-needle/needle/blob/master/needle/cases.py#L125

        :param str directory: Directory path to create
        :return:
        """

        try:

            os.makedirs(directory)

        except OSError as err:

            if err.errno == EEXIST and os.path.isdir(directory):
                return

            raise err

    def _find_element(self, element_or_selector=None):
        """Returns an element

        :param element_or_selector: WebElement or tuple containing selector ex. ('id', 'mainPage')
        :return:
        """

        if isinstance(element_or_selector, tuple):

            elements = self.driver.find_elements(*element_or_selector)
            return elements[0] if elements else None

        elif isinstance(element_or_selector, WebElement):
            return element_or_selector

    @staticmethod
    def _get_element_dimensions(element):
        """Returns an element's position and size

        :param WebElement element: Element to get dimensions for
        :return:
        """

        if isinstance(element, WebElement):

            # Get dimensions of element
            location = element.location
            size = element.size

            return {
                'top': int(location['y']),
                'left': int(location['x']),
                'width': int(size['width']),
                'height': int(size['height'])
            }

    def _get_element_rect(self, element):
        """Returns the two points that define the rectangle

        :param WebElement element: Element to get points for
        :return:
        """

        dimensions = self._get_element_dimensions(element)

        if dimensions:

            return (
                dimensions['left'],
                dimensions['top'],
                (dimensions['left'] + dimensions['width']),
                (dimensions['top'] + dimensions['height'])
            )

    @staticmethod
    def _get_ratio(image_size, window_size):

        return max((
            math.ceil(image_size[0] / float(window_size[0])),
            math.ceil(image_size[1] / float(window_size[1]))
        ))

    def _get_window_size(self):

        window_size = self.driver.get_window_size()
        return window_size['width'], window_size['height']

    @property
    def baseline_dir(self):
        """Return baseline image path

        :return:
        :rtype: str
        """

        return self.options.get('baseline_dir', DEFAULT_BASELINE_DIR)

    @baseline_dir.setter
    def baseline_dir(self, value):
        """Set baseline image directory

        :param str value: File path
        :return:
        """

        assert isinstance(value, basestring)
        self.options['baseline_dir'] = value

    @property
    def cleanup_on_success(self):
        """Returns True, if cleanup on success flag is set

        :return:
        :rtype: bool
        """

        return self.options.get('cleanup_on_success', False)

    @cleanup_on_success.setter
    def cleanup_on_success(self, value):
        """Set cleanup on success flag

        :param bool value: Cleanup on success flag
        :return:
        """

        self.options['cleanup_on_success'] = bool(value)

    @property
    def engine(self):
        """Return image processing engine

        :return:
        """

        return import_from_string(self.engine_class)()

    @property
    def engine_class(self):
        """Return image processing engine name

        :return:
        :rtype: str
        """

        return self.ENGINES.get(self.options.get('needle_engine', 'pil').lower(), DEFAULT_ENGINE)

    @engine_class.setter
    def engine_class(self, value):
        """Set image processing engine name

        :param str value: Image processing engine name (pil, imagemagick, perceptualdiff)
        :return:
        """

        assert value.lower() in self.ENGINES
        self.options['needle_engine'] = value.lower()

    def get_screenshot(self, element=None):
        """Returns screenshot image

        :param WebElement element: Crop image to element (Optional)
        :return:
        """

        stream = IOClass(base64.b64decode(self.driver.get_screenshot_as_base64().encode('ascii')))
        image = Image.open(stream).convert('RGB')

        if isinstance(element, WebElement):

            window_size = self._get_window_size()

            image_size = image.size

            # Get dimensions of element
            dimensions = self._get_element_dimensions(element)

            if not image_size == (dimensions['width'], dimensions['height']):

                ratio = self._get_ratio(image_size, window_size)

                return image.crop([point * ratio for point in self._get_element_rect(element)])

        return image

    def get_screenshot_as_image(self, element=None, exclude=None):
        """

        :param WebElement element: Crop image to element (Optional)
        :param list exclude: Elements to exclude
        :return:
        """

        image = self.get_screenshot(element)

        # Mask elements in exclude if element is not included
        if isinstance(exclude, (list, tuple)) and exclude and not element:

            # Gather all elements to exclude
            elements = [self._find_element(element) for element in exclude]
            elements = [element for element in elements if element]

            canvas = ImageDraw.Draw(image)

            window_size = self._get_window_size()

            image_size = image.size

            ratio = self._get_ratio(image_size, window_size)

            for ele in elements:
                canvas.rectangle([point * ratio for point in self._get_element_rect(ele)],
                                 fill=ImageColor.getrgb('black'))

            del canvas

        return image

    def assert_screenshot(self, file_path, element_or_selector=None, threshold=0, exclude=None):
        """Fail if new fresh image is too dissimilar from the baseline image

        .. note:: From needle
            https://github.com/python-needle/needle/blob/master/needle/cases.py#L161

        :param str file_path: File name for baseline image
        :param element_or_selector: WebElement or tuple containing selector ex. ('id', 'mainPage')
        :param threshold: Distance threshold
        :param list exclude: Elements or element selectors for areas to exclude
        :return:
        """

        element = self._find_element(element_or_selector)

        # Get fresh screenshot
        fresh_image = self.get_screenshot_as_image(element, exclude=exclude)
        fresh_image_file = os.path.join(self.output_dir, '%s.png' % file_path)
        fresh_image.save(fresh_image_file)

        # Get baseline image
        if isinstance(file_path, basestring):
            baseline_image = os.path.join(self.baseline_dir, '%s.png' % file_path)
            if self.save_baseline:

                if self.cleanup_on_success:
                    os.remove(fresh_image_file)

                # Take screenshot and exit
                return self.get_screenshot_as_image(element, exclude=exclude).save(baseline_image)

            if not self.save_baseline and not os.path.exists(baseline_image):
                raise IOError('The baseline screenshot %s does not exist. You might want to '
                              're-run this test in baseline-saving mode.' % baseline_image)

        else:
            # Comparing in-memory files instead of on-disk files
            baseline_image = Image.open(file_path).convert('RGB')

        # Compare images
        if isinstance(baseline_image, basestring):
            try:
                self.engine.assertSameFiles(fresh_image_file, baseline_image, threshold)

            except AssertionError as err:
                msg = err.message \
                    if hasattr(err, "message") \
                    else err.args[0] if err.args else ""
                args = err.args[1:] if len(err.args) > 1 else []
                raise ImageMismatchException(
                    msg, baseline_image, fresh_image_file, args)

            finally:
                if self.cleanup_on_success:
                    os.remove(fresh_image_file)

        else:

            diff = ImageDiff(fresh_image, baseline_image)
            distance = abs(diff.get_distance())

            if distance > threshold:
                pytest.fail('Fail: New screenshot did not match the '
                            'baseline (by a distance of %.2f)' % distance)

    @property
    def output_dir(self):
        """Return output image path

        :return:
        :rtype: str
        """

        return self.options.get('output_dir', DEFAULT_OUTPUT_DIR)

    @output_dir.setter
    def output_dir(self, value):
        """Set output image directory

        :param str value: File path
        :return:
        """

        assert isinstance(value, basestring)
        self.options['output_dir'] = value

    @property
    def save_baseline(self):
        """Returns True, if save baseline flag is set

        :return:
        :rtype: bool
        """

        return self.options.get('save_baseline', False)

    @save_baseline.setter
    def save_baseline(self, value):
        """Set save baseline flag

        :param bool value: Save baseline flag
        :return:
        """

        self.options['save_baseline'] = bool(value)

    @property
    def viewport_size(self):
        """Return setting for browser window size

        :return:
        :rtype: str
        """

        return self.options.get('viewport_size', DEFAULT_VIEWPORT_SIZE)

    @viewport_size.setter
    def viewport_size(self, value):
        """Set setting for browser window size

        :param value: Browser window size, as string or (x,y)
        :return:
        """

        assert isinstance(value, (basestring, list, tuple))
        assert len(value) == 2 and all([isinstance(i, int) for i in value]) \
            if isinstance(value, (list, tuple)) else True
        self.options['viewport_size'] = value if isinstance(value, basestring) else '{}x{}'.format(*value)
