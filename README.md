# PyAER

[![GitHub release](https://img.shields.io/github/release/duguyue100/pyaer.svg?style=flat-square)](https://github.com/duguyue100/pyaer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyaer.svg?style=flat-square)](https://pypi.org/project/pyaer/)
[![Build Status](https://api.travis-ci.org/duguyue100/pyaer.svg?branch=master)](https://travis-ci.org/duguyue100/pyaer)
[![Build status](https://ci.appveyor.com/api/projects/status/uf13jm7690abu11i/branch/master?svg=true)](https://ci.appveyor.com/project/duguyue100/pyaer/branch/master)
[![license](https://img.shields.io/github/license/duguyue100/pyaer.svg)](https://github.com/duguyue100/pyaer/blob/master/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1419354.svg)](https://doi.org/10.5281/zenodo.1419354)

![Ubuntu](https://img.shields.io/badge/OS-Ubuntu-orange.svg)
![macOS](https://img.shields.io/badge/OS-macOS-orange.svg)
![Raspbian](https://img.shields.io/badge/OS-Raspbian%20Stretch-orange.svg)
![Windows](https://img.shields.io/badge/OS-Windows-orange.svg)

PyAER with Swig Bindings

Special thanks to [iniLabs](http://inilabs.com/) for making this possible.

The project is in its Beta development stage, please submit an [issue](https://github.com/duguyue100/pyaer/issues) if you need our help.

Check out the [documentation](https://dgyblog.com/pyaer-doc/) for more help!

## Design Principle

+ Minimum installation effort
+ Clean, simple, easy to manage
+ Well documented, human-readable code

## Installation

1. Install `libcaer` dependency (RECOMMEND)

    ```bash
    $ bash <(curl -s https://raw.githubusercontent.com/duguyue100/pyaer/master/install-libcaer.sh)
    ```

    __NOTE:__ To build `libcaer` on Windows, please follow [this description](https://github.com/inilabs/libcaer/blob/master/README.Windows).

    __NOTE:__ For more information, see [`libcaer` repo](https://github.com/inilabs/libcaer).

    __NOTE:__ From 0.1.0a18, we support eDVS, you will need to install `libserialport` so that the package can work properly, follow the building instructions from [here](https://sigrok.org/wiki/Libserialport). Currently, this support is not built into the release since we are not clear how useful is this feature. If you are interested, you can build the project from scratch.

2. Install `pyaer` from pypi (RECOMMEND)

    ```bash
    $ pip install pyaer
    ```

3. Install from source

    ```
    $ git clone https://github.com/duguyue100/pyaer.git
    $ make install
    ```

## Got a Linux? [Optional]

__NOTE__: The `libcaer` installation has taken care of this problem.
However, if the problem persists, please try following.

`libcaer` relies on `libusb` based driver, you won't be able
to access the camera unless fixing the `udev` rules. Refer to details
at [here](https://inivation.com/support/hardware/davis240/#linux).

```bash
$ bash <(curl -s https://raw.githubusercontent.com/duguyue100/pyaer/master/install-udev.sh)
```

## Running Examples

The [scripts](./scripts) folder provides some examples for you to play with:

1. `dvs128-test`: you need OpenCV to run this example, note that if you are on Mac, OpenCV's `waitKey()` function may cause delay of displaying frames.

2. `dvs128-glumpy`: you need `glumpy` package to run this example. `glumpy` is a fast visualization library based on OpenGL. We found it's very fast to render images. In our case, we use GLFW backend. If `glumpy` couldn't find your installed GLFW on your system, make sure you set the `GLFW_LIBRARY` variable to `/your/glfw/library/path/libglfw.so`.

3. `dvs240-test`: you need OpenCV to run this example.

4. `dvs346-test`: you need OpenCV to run this example.

More examples are coming...

## Yeah, you need SWIG

__You only need to read this section if you are planning to compile
`pyaer` from source.__

This repository uses SWIG to create Python bindings. And you will need to
compile the latest SWIG from source. The reason is because current SWIG
cannot handle some cases in libcaer, we made a modified SWIG for this purpose.

1. Install compilation dependency

    ```
    $ sudo apt-get install automake
    $ sudo apt-get install bison
    ```

    _There might be other dependencies for compiling SWIG_

2. Compile SIWG

    ```
    $ git clone https://github.com/duguyue100/swig
    $ cd swig
    $ ./autogen.sh
    $ ./configure
    $ make
    $ sudo make install
    ```

    For compiling SWIG with Python

    ```
    $ ./configure --without-alllang --with-python=$(command -v python)
    ```

    __NOTE:__ Make sure the `python` is pointed to the correct `python3` binary
    if you would like to use Python 3.

    __NOTE:__ For Windows, consider append `--without-pcre` if the `./configure`
    doesn't work properly.

    __NOTE:__ If you are not compile the SWIG with system Python distribution,
    it won't link to the custom Python automatically.

    You will need to configure `LD_LIBRARY_PATH` for swig running properly.

    e.g.

    ```
    LD_LIBRARY_PATH=$HOME/anaconda2/lib:$LD_LIBRARY_PATH swig
    ```

## Limitations and Notes

+ Current status of the project is meant for single device use. Potentially,
this library supports multiple devices at the same time by giving concrete
device names and serial numbers. Supporting and testing for multiple devices
setup is in long-term plan, but we are not working on this right now.

+ Once the data stream is open, the data will be streamed through USB connection
at certain publishing frequency (e.g. 100Hz). This is a hardware configuration,
therefore you couldn't drop event packets by putting software-level delay.
You can either skip processing the coming packets by some conditions or
implement a queuing system that can do a particular dynamic fetching.

+ It's recommended to implement a multi-processing or multi-threading
program so that each process or thread only deals with one particular task.
The fetching of the event packets may be very fast, your program may be delayed
if you are not carefully coping with this fact.

+ DYNAP is generally supported. We are currently looking for the correct
bias configuration mechanism so that it can easily support the use of the
device. We have mapped some core functions that are essential to device
configuration.

## Contacts

Yuhuang Hu  
Email: duguyue100@gmail.com
