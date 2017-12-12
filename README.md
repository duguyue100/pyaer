# PyAER

PyAER with Swig Bindings

Special thanks to [iniLabs](http://inilabs.com/) to make this possible.

+ Supported platform: `Ubuntu`
+ Supported Python: 2.7

__WARNING: This project needs bleeding-edge SWIG and a custom fix.
If you are still interested, pleast contact us.__

## Design Principle

+ Minimum installation effort
+ Keep active development in mind
+ Keep Python 2 and 3 in mind, however prioritize Python 2 first
+ Clean, simple, easy to manage
+ Well documented, human-readable code
+ Let's not do Windows for this moment
+ Let's not do Mac for this moment

## TODO

+ [ ] Intermediate level API for accessing camera
+ [ ] Support Python 3
+ [ ] Testing compilation script
+ [ ] Can we provide pre-built binaries?

## Installation

1. Install `libcaer` dependency

```
$ sudo apt-get install libusb-1.0-0-dev
```

__NOTE:__ For more information, see [`libcaer` repo](https://github.com/inilabs/libcaer).

2. Download this repo

```
$ git clone --recursive https://github.com/duguyue100/pyaer-beta.git
```

3. Change `compile.conf.bak` to `compile.conf` and configure Python executable

```
cd pyaer-beta
cp compile.conf.bak compile.conf
```

The configuration file looks like

```bash
# Turn it to true if you are building the repository for the first time
REBUILDING=false

# defien python version (experimental)
# only support python 2 at this moment
PYTHON_VERSION=2

# define python executable
CONDA_LIB_PATH=$HOME/anaconda2/lib
CONDA_PKG_CONFIG_PATH=$CONDA_LIB_PATH/pkgconfig

# false if build libcaer locally
# true  if you have a system installed libcaer
LIBCAER_INSTALLED=false
```

4. Make this repository and install it!

```
$ ./compile make
$ ./compile make.install
```

__NOTE:__ This repository is designed to be compiled and run within local
directory, nothing to pollute your system because this is in active
development.

5. (Optional) if you want to clean the installation, just type

```
$ ./compile clean
```

6. (Optional) The available commands for the compilation script are:

+ `make`: make `libcaer` and SWIG binding
+ `make.swig`: make SWIG binding only
+ `make.lib` : make `libcaer`
+ `make.install`: Install compiled wrapper to the package
+ `clean`: clean SWIG compilation, `libcaer` and installation
+ `clean.swig`: clean SWIG
+ `clean.lib` : clean `libcaer` compilation
+ `clean.install` : clean installation
+ `help`: print help info

## Yeah, you need SWIG

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
$ ./configure --with-python=${command -v python} --without-python3
```

The above is an example with Python 2, you can configure for Python 3 as well

```
$ ./configure --with-python=${command -v python} --without-python2
```

__Note:__ If you are not compile the SWIG with system Python distribution,
it won't link to the custom Python automatically.

You will need to configure `LD_LIBRARY_PATH` for swig running properly.

e.g.

```
LD_LIBRARY_PATH=$HOME/anaconda2/lib:$LD_LIBRARY_PATH swig
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

## Contacts

Yuhuang Hu  
Email: duguyue100@gmail.com
