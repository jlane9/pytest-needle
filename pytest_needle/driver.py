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
from PIL import Image
from selenium.webdriver.remote.webdriver import WebElement


if sys.version_info >= (3, 0):
    from io import BytesIO as IOClass
    basestring = str

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

        # Determine viewport width and height
        dimensions = kwargs.get('viewport_size', DEFAULT_VIEWPORT_SIZE)
        viewport_size = re.match(r'(?P<width>\d+)\s?[xX]\s?(?P<height>\d+)', dimensions)

        if viewport_size:
            self.viewport_width = int(viewport_size.group('width'))
            self.viewport_height = int(viewport_size.group('height'))

        else:
            self.viewport_width = int(DEFAULT_VIEWPORT_SIZE.split('x')[0])
            self.viewport_height = int(DEFAULT_VIEWPORT_SIZE.split('x')[1])

        # Set viewport position, size
        self.driver.set_window_position(0, 0)
        self.set_viewport_size(self.viewport_width, self.viewport_height)

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

    def set_viewport_size(self, width, height):
        """Readjust viewport to size specified

        .. note:: From needle
            https://github.com/python-needle/needle/blob/master/needle/cases.py#L151

        :param int width: Viewport width
        :param int height: Viewport height
        :return:
        """

        self.driver.set_window_size(width, height)

        measured = self.driver.execute_script(
            "return {width: document.body.clientWidth, height: document.body.clientHeight};")

        delta = width - measured['width']

        self.driver.set_window_size(width + delta, height)

    def get_screenshot_as_image(self, element=None):
        """Returns screenshot image

        :param element: Crop image to element (Optional)
        :return:
        """

        stream = IOClass(base64.b64decode(self.driver.get_screenshot_as_base64().encode('ascii')))
        image = Image.open(stream).convert('RGB')

        if element:

            window_size = (
                self.driver.get_window_size()['width'],
                self.driver.get_window_size()['height']
            )

            image_size = image.size

            # Get dimensions of element
            location = element.location
            size = element.size

            dimensions = {
                'top': int(location['y']),
                'left': int(location['x']),
                'width': int(size['width']),
                'height': int(size['height'])
            }

            if not image_size == (dimensions['width'], dimensions['height']):

                print image_size
                print window_size
                print dimensions

                ratio = max((
                    math.ceil(image_size[0]/float(window_size[0])),
                    math.ceil(image_size[1]/float(window_size[1]))
                ))

                print ratio

                return image.crop((
                    dimensions['left'] * ratio,
                    dimensions['top'] * ratio,
                    (dimensions['left'] + dimensions['width']) * ratio,
                    (dimensions['top'] + dimensions['height']) * ratio
                ))

        return image

    def assert_screenshot(self, file_path, element_or_selector=None, threshold=0):
        """Fail if new fresh image is too dissimilar from the baseline image

        .. note:: From needle
            https://github.com/python-needle/needle/blob/master/needle/cases.py#L161

        :param str file_path: File name for baseline image
        :param element_or_selector:
        :param threshold: Distance threshold
        :return:
        """

        if isinstance(element_or_selector, tuple):

            elements = self.driver.find_elements(*element_or_selector)
            element = elements[0] if elements else None

        else:
            element = element_or_selector if isinstance(element_or_selector, WebElement) else None

        if not isinstance(file_path, basestring):

            # Comparing in-memory files instead of on-disk files
            baseline_image = Image.open(file_path).convert('RGB')

            fresh_image = self.get_screenshot_as_image(element)

            diff = ImageDiff(fresh_image, baseline_image)
            distance = abs(diff.get_distance())

            if distance > threshold:
                pytest.fail('Fail: New screenshot did not match the '
                            'baseline (by a distance of %.2f)' % distance)

        else:

            baseline_file = os.path.join(self.baseline_dir, '%s.png' % file_path)
            output_file = os.path.join(self.output_dir, '%s.png' % file_path)

            if self.save_baseline:

                # Take screenshot and exit
                return self.get_screenshot_as_image(element).save(baseline_file)

            else:

                if not os.path.exists(baseline_file):
                    raise IOError('The baseline screenshot %s does not exist. '
                                  'You might want to re-run this test in baseline-saving mode.'
                                  % baseline_file)

                # Save the new screenshot
                self.get_screenshot_as_image(element).save(output_file)

                try:
                    self.engine.assertSameFiles(output_file, baseline_file, threshold)

                except:
                    raise

                finally:
                    if self.cleanup_on_success:
                        os.remove(output_file)
