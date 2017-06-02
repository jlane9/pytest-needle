"""setup.py

.. codeauthor:: John Lane <jlane@fanthreesixty.com>

"""

from setuptools import setup
from pytest_needle import __author__, __email__, __license__, __version__


setup(name='pytest-needle',
      version=__version__,
      description='pytest plugin for visual testing websites using selenium',
      author=__author__,
      author_email=__email__,
      url=u'https://github.com/jlane9/pytest-needle',
      packages=['pytest_needle'],
      entry_points={'pytest11': ['needle = pytest_needle.plugin', ]},
      install_requires=['pytest>=2.7', 'needle'],
      keywords='py.test pytest needle imagemagick perceptualdiff pil selenium visual',
      license=__license__,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Framework :: Pytest',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: MacOS :: MacOS X',
          'Topic :: Software Development :: Testing',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
      ])
