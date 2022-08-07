"""Setup script for the pyaer package.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import
from setuptools import setup
from setuptools import find_packages
from setuptools.extension import Extension

import os
from sysconfig import get_paths
from sys import platform

import numpy

classifiers = """
Development Status :: 4 - Beta
Intended Audience :: Science/Research
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Topic :: Utilities
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Artificial Intelligence
Topic :: Software Development :: Libraries :: Python Modules
License :: OSI Approved :: MIT License
"""

try:
    from pyaer import __about__

    about = __about__.__dict__
except ImportError:
    about = dict()
    exec(open("pyaer/__about__.py").read(), about)

python_paths = get_paths()

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

if platform in ["linux", "linux2"]:
    libcaer_include = "/usr/include"
    libcaer_lib = "/usr/lib/x86_64-linux-gnu"

    # for Raspberry Pi support
    if os.uname()[1] == "raspberrypi":
        libcaer_lib = "/usr/lib/arm-linux-gnueabihf"
elif platform == "darwin":
    libcaer_include = "/usr/local/include"
    libcaer_lib = "/usr/local/lib"
elif "win" in platform:
    libcaer_include = "C:/msys64/mingw64/include"
    libcaer_lib = "C:/msys64/mingw64/lib"

libcaer_wrap = Extension(
    name="pyaer._libcaer_wrap",
    sources=["./pyaer/pyflags.i"],
    include_dirs=[libcaer_include, python_paths["include"], numpy_include],
    library_dirs=[libcaer_lib, python_paths["stdlib"]],
    swig_opts=["-I" + libcaer_include],
    #  extra_compile_args=["-std=c11"],
    extra_link_args=["-lcaer"],
)

setup(
    name="pyaer",
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    install_requires=["numpy >= 1.18.0"],
    packages=find_packages(),
    ext_modules=[libcaer_wrap],
    scripts=[
        "scripts/aer_comm/aer_hub",
        "scripts/aer_comm/aer_lstopic",
        "scripts/aer_comm/aer_publisher",
        "scripts/aer_comm/aer_subscriber",
        "scripts/aer_comm/aer_pubsuber",
        "scripts/aer_comm/aer_launch",
        "scripts/aer_comm/aer_saver",
    ],
    classifiers=list(filter(None, classifiers.split("\n"))),
    description="PyAER: Low-level Python APIs for Accessing Neuromorphic Devices.",
)
