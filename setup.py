"""setup.py

.. codeauthor:: John Lane <jlane@fanthreesixty.com>

"""

import os
from setuptools import setup
from pytest_needle import __author__, __email__, __license__, __version__


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(name='pytest-needle',
      version=__version__,
      author=__author__,
      author_email=__email__,
      description='pytest plugin for visual testing websites using selenium',
      license=__license__,
      keywords='py.test pytest needle imagemagick perceptualdiff pil selenium visual',
      url=u'https://github.com/jlane9/pytest-needle',
      project_urls={
          "Documentation": "https://pytest-needle.readthedocs.io/en/latest/",
          "Tracker": "https://github.com/jlane9/pytest-needle/issues"
      },
      packages=['pytest_needle'],
      entry_points={'pytest11': ['needle = pytest_needle.plugin', ]},
      long_description=read("README.md"),
      long_description_content_type="text/markdown",
      install_requires=[
          'pytest>=3.7.0,<6.0.0',
          'needle>=0.5.0,<0.6.0',
          'pytest-selenium>=1.16.0,<2.0.0'
      ],
      python_requires=">=2.7",
      tests_require=[
          "pytest-cov>=2.7.0",
          "python-coveralls>=2.9.0",
          "pytest-pep8>=1.0.0"
      ],
      extras_require={
          "release": [
              "bumpversion>=0.5.0",
              "recommonmark>=0.5.0",
              "Sphinx>=1.8.0",
              "sphinx-autobuild>=0.7.0",
              "sphinx-rtd-theme>=0.4.0",
          ]
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Pytest',
          'Intended Audience :: Developers',
          "Natural Language :: English",
          'Operating System :: POSIX',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
          'Topic :: Utilities'
      ])
