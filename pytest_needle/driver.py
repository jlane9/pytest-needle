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

        self.save_baseline = kwargs.get('save_baseline', False)
        self.cleanup_on_success = kwargs.get('cleanup_on_success', False)

        self.baseline_dir = kwargs.get('baseline_dir', DEFAULT_BASELINE_DIR)
        self.output_dir = kwargs.get('output_dir', DEFAULT_OUTPUT_DIR)

        # Create the output and baseline directories if they do not yet exist.
        for directory in (self.baseline_dir, self.output_dir):
            self._create_dir(directory)

        dimensions = kwargs.get('viewport_size', DEFAULT_VIEWPORT_SIZE)
        viewport_size = re.match(r'(?P<width>\d+)\s?[xX]\s?(?P<height>\d+)', dimensions)

        # Set viewport position, size
        self.driver.set_window_position(0, 0)
        viewport_dimensions = (int(viewport_size.group('width')), int(viewport_size.group('height'))) if viewport_size \
            else (int(DEFAULT_VIEWPORT_SIZE.split('x')[0]), int(DEFAULT_VIEWPORT_SIZE.split('x')[1]))

        self.driver.set_window_size(*viewport_dimensions)

        # Instantiate the diff engine
        engine_config = kwargs.get('needle_engine', 'pil').lower()
        self.engine_class = self.ENGINES.get(engine_config, DEFAULT_ENGINE)

        klass = import_from_string(self.engine_class)
        self.engine = klass()

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

        return element_or_selector if isinstance(element_or_selector, WebElement) else None

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

    def get_screenshot(self, element=None):
        """Returns screenshot image

        :param WebElement element: Crop image to element (Optional)
        :return:
        """

        stream = IOClass(base64.b64decode(self.driver.get_screenshot_as_base64().encode('ascii')))
        image = Image.open(stream).convert('RGB')

        if isinstance(element, WebElement):

            window_size = (
                self.driver.get_window_size()['width'],
                self.driver.get_window_size()['height']
            )

            image_size = image.size

            # Get dimensions of element
            dimensions = self._get_element_dimensions(element)

            if not image_size == (dimensions['width'], dimensions['height']):

                ratio = max((
                    math.ceil(image_size[0]/float(window_size[0])),
                    math.ceil(image_size[1]/float(window_size[1]))
                ))

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

            window_size = (
                self.driver.get_window_size()['width'],
                self.driver.get_window_size()['height']
            )

            image_size = image.size

            ratio = max((
                math.ceil(image_size[0] / float(window_size[0])),
                math.ceil(image_size[1] / float(window_size[1]))
            ))

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

        # Get baseline image
        if isinstance(file_path, basestring):

            baseline_image = os.path.join(self.baseline_dir, '%s.png' % file_path)

            if self.save_baseline:

                # Take screenshot and exit
                return self.get_screenshot_as_image(element, exclude=exclude).save(baseline_image)

            else:

                if not os.path.exists(baseline_image):
                    raise IOError('The baseline screenshot %s does not exist. '
                                  'You might want to re-run this test in baseline-saving mode.'
                                  % baseline_image)

        else:

            # Comparing in-memory files instead of on-disk files
            baseline_image = Image.open(file_path).convert('RGB')

        # Get fresh screenshot
        fresh_image = self.get_screenshot_as_image(element, exclude=exclude)

        # Compare images
        if isinstance(baseline_image, basestring):

            output_file = os.path.join(self.output_dir, '%s.png' % file_path)
            fresh_image.save(output_file)

            try:
                self.engine.assertSameFiles(output_file, baseline_image, threshold)

            except AssertionError as err:
                raise ImageMismatchException(err.message, baseline_image, output_file)

            finally:
                if self.cleanup_on_success:
                    os.remove(output_file)

        else:

            diff = ImageDiff(fresh_image, baseline_image)
            distance = abs(diff.get_distance())

            if distance > threshold:
                pytest.fail('Fail: New screenshot did not match the '
                            'baseline (by a distance of %.2f)' % distance)
