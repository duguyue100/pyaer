![PyAER](./res/pyaer_cover_img.png)

---

[![GitHub release](https://img.shields.io/github/release/duguyue100/pyaer.svg?style=flat-square)](https://github.com/duguyue100/pyaer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyaer.svg?style=flat-square)](https://pypi.org/project/pyaer/)
[![Build Status](https://api.travis-ci.org/duguyue100/pyaer.svg?branch=master)](https://travis-ci.org/duguyue100/pyaer)
[![license](https://img.shields.io/github/license/duguyue100/pyaer.svg)](https://github.com/duguyue100/pyaer/blob/master/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1346279.svg)](https://doi.org/10.5281/zenodo.1346279)

![Linux](https://img.shields.io/badge/OS-Linux-orange.svg)
![macOS](https://img.shields.io/badge/OS-macOS-orange.svg)
![AMD64](https://img.shields.io/badge/ARCH-AMD64-orange.svg)
![ARM](https://img.shields.io/badge/ARCH-ARM64-orange.svg)

![DVS128](https://img.shields.io/badge/DEVICE-DVS128-blueviolet.svg)
![eDVS](https://img.shields.io/badge/DEVICE-eDVS-blueviolet.svg)
![DVS240C](https://img.shields.io/badge/DEVICE-DVS240C-blueviolet.svg)
![DVS346](https://img.shields.io/badge/DEVICE-DVS346-blueviolet.svg)
![DVXLite](https://img.shields.io/badge/DEVICE-DVXplorer%20Lite-blueviolet.svg)
![DVX](https://img.shields.io/badge/DEVICE-DVXplorer-blueviolet.svg)
![EVK](https://img.shields.io/badge/DEVICE-Samsung%20EVK-blueviolet.svg)

Special thanks to [iniVation](https://inivation.com/) for making this possible!

The project is in its Beta development stage, please submit an [issue](https://github.com/duguyue100/pyaer/issues) if you encountered a problem.

For ARM wheels, please check out the [Releases](https://github.com/duguyue100/pyaer/releases).

## Why PyAER?

iniVation has released [DV](https://gitlab.com/inivation/dv), a new platform and an SDK for accessing and developing with event cameras.

For robotics projects, you may find [rpg_dvs_ros](https://github.com/uzh-rpg/rpg_dvs_ros) when you use ROS.

So the natural question is: why PyAER?

In a nutshell, PyAER is a combination of a Pythonic `libcaer` and a light-weight "ROS". PyAER serves as an agile package that focus on fast development and extensibility. In fact, in some scenario, e.g., edge devices, PyAER is more user friendly than other alternatives.

### Design Principle

+ Minimum installation effort.
+ Clean, simple, easy to manage.
+ Well documented, human-readable code.

## Installation

1. Install `libcaer` dependency (RECOMMEND)

    ```bash
    $ bash <(curl -s https://raw.githubusercontent.com/duguyue100/pyaer/master/install-libcaer.sh)
    ```

    Update `udev` rules if you use a Linux system:

    ```bash
    $ bash <(curl -s https://raw.githubusercontent.com/duguyue100/pyaer/master/install-udev.sh)
    ```

    __NOTE__: The `libcaer` installation has taken care of this update.
    However, if the problem persists, please try it.

2. Install `pyaer` from pypi (RECOMMEND)

    ```bash
    $ pip install pyaer
    ```

3. Install `pyzmq`
    ```
    $ pip install pyzmq
    ```

    __NOTE:__ `pyzmq` is not available on ARM-based computer, you will need to build yourself.

### Development

For development purpose, you might build `pyaer` from source.
Please follow the instructions in [INSTALL_FROM_SOURCE.md](./INSTALL_FROM_SOURCE.md)

## Running Examples

The [scripts](./scripts) folder provides some examples for you to play with:

1. `dvs128-test`: you need OpenCV to run this example, note that if you are on Mac, OpenCV's `waitKey()` function may cause delay of displaying frames.

2. `dvs240-test`: you need OpenCV to run this example.

3. `dvs346-test`: you need OpenCV to run this example.

More examples are coming...

## Limitations and Notes

+ __2020-12-10__: From 0.2.1, we support experimental interfaces for
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
