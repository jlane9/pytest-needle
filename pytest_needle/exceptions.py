"""exceptions

.. codeauthor: John Lane <jlane@fanthreesixty.com>

"""


class NeedleException(AssertionError):
    """Base exception for pytest-needle
    """


class ImageMismatchException(NeedleException):
    """Image mismatch exception
    """

    def __init__(self, message, baseline_image, output_image, *args):

        self.baseline_image = baseline_image
        self.output_image = output_image

        super(ImageMismatchException, self).__init__(message, *args)


class MissingBaselineException(NeedleException):
    """Missing baseline exception
    """

    def __init__(self, message, *args):

        super(MissingBaselineException, self).__init__(message, *args)


class MissingEngineException(NeedleException):
    """Missing engine exception
    """

    def __init__(self, message, *args):

        super(MissingEngineException, self).__init__(message, *args)
