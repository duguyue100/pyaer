![PyAER](./res/pyaer_cover_img.png)

---

[![GitHub release](https://img.shields.io/github/release/duguyue100/pyaer.svg?style=flat-square)](https://github.com/duguyue100/pyaer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyaer.svg?style=flat-square)](https://pypi.org/project/pyaer/)
[![Build Status](https://api.travis-ci.org/duguyue100/pyaer.svg?branch=master)](https://travis-ci.org/duguyue100/pyaer)
[![license](https://img.shields.io/github/license/duguyue100/pyaer.svg)](https://github.com/duguyue100/pyaer/blob/master/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1419354.svg)](https://doi.org/10.5281/zenodo.1419354)

![Linux](https://img.shields.io/badge/OS-Linux-orange.svg)
![macOS](https://img.shields.io/badge/OS-macOS-orange.svg)
![ARM](https://img.shields.io/badge/ARCH-ARM-orange.svg)

![DVS128](https://img.shields.io/badge/DEVICE-DVS128-blueviolet.svg)
![eDVS](https://img.shields.io/badge/DEVICE-eDVS-blueviolet.svg)
![DVS240C](https://img.shields.io/badge/DEVICE-DVS240C-blueviolet.svg)
![DVS346](https://img.shields.io/badge/DEVICE-DVS346-blueviolet.svg)
![DVXLite](https://img.shields.io/badge/DEVICE-DVXplorer%20Lite-blueviolet.svg)
![DVX](https://img.shields.io/badge/DEVICE-DVXplorer-blueviolet.svg)
![EVK](https://img.shields.io/badge/DEVICE-Samsung%20EVK-blueviolet.svg)

PyAER with Swig Bindings

Special thanks to [iniVation](https://inivation.com/) for making this possible.

The project is in its Beta development stage, please submit an [issue](https://github.com/duguyue100/pyaer/issues) if you need our help.

Check out the [documentation](https://dgyblog.com/pyaer-doc/) for more help!

## Why PyAER?

iniVation has released [DV](https://gitlab.com/inivation/dv), a new platform and an SDK for accessing and developing with event cameras.

For robotics projects, you may find [rpg_dvs_ros](https://github.com/uzh-rpg/rpg_dvs_ros) when you use ROS.

So the natural question is: why PyAER?

Although there are large function overlaps between these frameworks, PyAER serves as an agile package that focus on fast development and extensibility. In fact, in some scenario, e.g. edge devices, PyAER is more user friendly than other alternatives.

### Design Principle

+ Minimum installation effort.
+ Clean, simple, easy to manage.
 Well documented, human-readable code.

## Installation

1. Install `libcaer` dependency (RECOMMEND)

    ```bash
    $ bash <(curl -s https://raw.githubusercontent.com/duguyue100/pyaer/master/install-libcaer.sh)
    ```

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

2. `dvs240-test`: you need OpenCV to run this example.

3. `dvs346-test`: you need OpenCV to run this example.

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

    __NOTE:__ If you are not compile the SWIG with system Python distribution,
    it won't link to the custom Python automatically.

    You will need to configure `LD_LIBRARY_PATH` for swig running properly.

    i.e.

    ```
    LD_LIBRARY_PATH=$HOME/anaconda2/lib:$LD_LIBRARY_PATH swig
    ```

## Limitations and Notes

+ __2020-12-10__: From 0.2.1, we will support experimental interfaces for
DVXplorer, DVXplorer Lite, and Samsung EVK. We will test these interfaces
if we manage to get physical devices. Otherwise, we welcome community
tests and improvements.

+ __2020-12-02__: From 0.2.0, we support a `zeromq`-based communication
module that allow users to leverage multiple processes during development.
It should be able to support multiple devices and concurrent logging and
visualization (haven't tested). If you are familiar with ROS, you should
find this feature very comfortable.

+ DYNAP is generally supported. We are currently looking for the correct
bias configuration mechanism so that it can easily support the use of the
device. We have mapped some core functions that are essential to device
configuration.

## Contacts

Yuhuang Hu  
Email: duguyue100@gmail.com
