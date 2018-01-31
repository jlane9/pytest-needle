#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""exceptions

.. codeauthor: John Lane <jlane@fanthreesixty.com>

"""


class NeedleException(AssertionError):
    """Base exception for pytest-needle
    """

    pass


class ImageMismatchException(NeedleException):
    """Image mismatch exception
    """

    def __init__(self, message, baseline_image, output_image, *args):

        self.baseline_image = baseline_image
        self.output_image = output_image

        super(ImageMismatchException, self).__init__(message, *args)
