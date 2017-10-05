"""Setup script for the pyaer package.

Author: Yuhuang Hu
Email : yuhuang.hu@uzh.ch
"""

from setuptools import setup

classifiers = """
Development Status :: 4 - Beta
Intended Audience :: Science/Research
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python :: 2.7
Topic :: Utilities
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Image Recognition
Topic :: Scientific/Engineering :: Visualization
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

    packages=["pyaer"],

    classifiers=list(filter(None, classifiers.split('\n'))),
    description="PyAER: Python bindings for Neuromorphic devices."
)
