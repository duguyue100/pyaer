# PyAER

[![Build Status](https://api.travis-ci.org/duguyue100/pyaer.svg?branch=master)](https://travis-ci.org/duguyue100/pyaer)

PyAER with Swig Bindings

Special thanks to [iniLabs](http://inilabs.com/) to make this possible.

+ Supported platform: `Ubuntu`
+ Supported Python: 2.7

## Design Principle

+ Minimum installation effort
+ Keep active development in mind
+ Keep Python 2 and 3 in mind, however prioritize Python 2 first
+ Clean, simple, easy to manage
+ Well documented, human-readable code
+ Let's not do Windows for this moment
+ Let's not do Mac for this moment

## Installation

1. Install `libcaer` dependency

```
$ sudo apt-get install libusb-1.0-0-dev
$ git clone https://github.com/inilabs/libcaer.git
$ cd libcaer
$ cmake -DCMAKE_INSTALL_PREFIX=/usr .
$ make
# make install
```

__NOTE:__ For more information, see [`libcaer` repo](https://github.com/inilabs/libcaer).

2. Directly install from pip (RECOMMEND)

```bash
#  for python 2.7
$ pip install https://github.com/duguyue100/pyaer/releases/download/0.1.0a7/pyaer-0.1.0a7-cp27-cp27mu-linux_x86_64.whl
```

``` bash
#  for python 3.6
$ pip install https://github.com/duguyue100/pyaer/releases/download/0.1.0a7/pyaer-0.1.0a7-cp36-cp36m-linux_x86_64.whl
```

3. Install from source

```
$ git clone https://github.com/duguyue100/pyaer-beta.git
$ make install
```

## Got a Linux?

`libcaer` relies on `libusb` based driver, you won't be able
to access the camera unless fix the `udev` rules. Refer details
from [here](https://inilabs.com/support/hardware/davis240/#h.eok9q1yrz7px)

```
$ sudo touch /etc/udev/rules.d/65-inilabs.rules
```

Append following contents in the file with `sudo`

```
# All DVS/DAVIS systems
SUBSYSTEM=="usb", ATTR{idVendor}=="152a", ATTR{idProduct}=="84[0-1]?", MODE="0666"
# eDVS 4337
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6014", MODE="0666"
```

Updating rules

```
$ udevadm control --reload
```

Unplug and replug the camera, you should be fine.

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
$ ./configure --with-python=$(command -v python) --without-python3
```

The above is an example with Python 2, you can configure for Python 3 as well

```
$ ./configure --with-python=$(command -v python) --without-python2
```

__Note:__ If you are not compile the SWIG with system Python distribution,
it won't link to the custom Python automatically.

You will need to configure `LD_LIBRARY_PATH` for swig running properly.

e.g.

```
LD_LIBRARY_PATH=$HOME/anaconda2/lib:$LD_LIBRARY_PATH swig
```

## Contacts

Yuhuang Hu  
Email: duguyue100@gmail.com
