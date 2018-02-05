"""Setup script for the pyaer package.

Author: Yuhuang Hu
Email : yuhuang.hu@uzh.ch
"""
from __future__ import print_function, absolute_import
from setuptools import setup
from setuptools import find_packages

from distutils.core import Extension

from sysconfig import get_paths
from sys import platform

import numpy

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

__version__ = "0.1.0a17"
__author__ = "Yuhuang Hu"
__author_email__ = "duguyue100@gmail.com"
__url__ = "https://github.com/duguyue100/pyaer"

python_paths = get_paths()

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

if platform in ["linux", "linux2"]:
    libcaer_include = "/usr/include"
    libcaer_lib = "/usr/lib"
elif platform == "darwin":
    libcaer_include = "/usr/local/include"
    libcaer_lib = "/usr/local/lib"

libcaer_wrap = Extension(
    name="_libcaer_wrap",
    sources=["./pyaer/pyflags.i"],
    include_dirs=[libcaer_include,
                  python_paths["include"], numpy_include],
    library_dirs=[libcaer_lib,
                  python_paths["stdlib"]],
    swig_opts=["-I"+libcaer_include],
    extra_compile_args=["-std=c11"],
    extra_link_args=["-lcaer"])

setup(
    name="pyaer",
    version=__version__,

    author=__author__,
    author_email=__author_email__,

    url=__url__,

    install_requires=["numpy",
                      "future",
                      "scipy"],

    packages=find_packages(),

    ext_modules=[libcaer_wrap],

    classifiers=list(filter(None, classifiers.split("\n"))),
    description="PyAER: Low-level Python APIs for "
                "Accessing Neuromorphic Devices."
)
