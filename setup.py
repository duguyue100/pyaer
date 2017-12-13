"""Setup script for the pyaer package.

Author: Yuhuang Hu
Email : yuhuang.hu@uzh.ch
"""

from setuptools import setup
from setuptools import find_packages

from distutils.core import Extension

from sysconfig import get_paths

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

python_paths = get_paths()

libcaer_wrap = Extension(
    name="_libcaer_wrap",
    sources=["./pyaer/pyflags.i"],
    include_dirs=["/usr/include",
                  python_paths["include"]],
    library_dirs=["/usr/lib",
                  python_paths["stdlib"]],
    swig_opts=["-I/usr/include"],
    extra_compile_args=["-std=c11"],
    extra_link_args=["-lcaer"])

setup(
    name="pyaer",
    version=about["__version__"],

    author=about["__author__"],
    author_email=about["__author_email__"],

    url=about["__url__"],

    install_requires=["numpy",
                      "future"],

    packages=find_packages(),

    ext_modules=[libcaer_wrap],

    classifiers=list(filter(None, classifiers.split("\n"))),
    description="PyAER: Python bindings for Neuromorphic devices."
)
