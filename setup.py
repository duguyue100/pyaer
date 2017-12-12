"""Setup script for the pyaer package.

Author: Yuhuang Hu
Email : yuhuang.hu@uzh.ch
"""

from setuptools import setup
from setuptools import find_packages

classifiers = """
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python :: 2.7
Topic :: Utilities
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Neuromorphic Engineering
Topic :: Software Development :: Libraries :: Python Modules
License :: OSI Approved :: MIT License
"""

try:
    from pyaer import __about__
    about = __about__.__dict__
except ImportError:
    about = dict()
    exec(open("pyaer/__about__.py").read(), about)

setup(
    name='pyaer',
    version=about["__version__"],

    author=about["__author__"],
    author_email=about["__author_email__"],

    url=about["__url__"],

    packages=find_packages(),

    classifiers=list(filter(None, classifiers.split('\n'))),
    description="PyAER: Python bindings for Neuromorphic devices."
)
