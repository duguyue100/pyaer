# PyAER-beta

PyAER with Swig Bindings

Special thanks to [iniLabs](http://inilabs.com/) to make this possible.

+ Supported platform: `Ubuntu`
+ Supported Python: 2.7

## TODO

+ [ ] Intermediate level API for accessing camera
+ [ ] Support Python 3
+ [ ] Testing compilation script

## Installation

1. Install `libcaer` dependency

```
$ sudo apt-get install libusb-1.0-9-dev
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

```
CONDA_LIB_PATH=$HOME/anaconda2/lib
CONDA_PKG_CONFIG_PATH=$CONDA_LIB_PATH/pkgconfig
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

## Yeah, you need SWIG

This repository uses SWIG to create Python bindings. And you will need to
compile the latest SWIG from source.

1. Install compilation dependency

```
$ sudo apt-get install automake
$ sudo apt-get install bison
```

_There might be other dependencies for compiling SWIG_

2. Compile SIWG

```
$ git clone https://github.com/swig/swig
$ cd swig
$ ./autogen.sh
$ ./configure
$ make
$ make install
```

For compiling SWIG with Anaconda

```
$ ./configure --with-python=/path/to/python/executable --without-python3
```

The above is an example with Python 2, you can configure for Python 3 as well

__Note:__ If you are not compile the SWIG with system Python distribution,
it won't link to the custom Python automatically.

You will need to configure `LD_LIBRARY_PATH` for swig running properly.

e.g.

```
LD_LIBRARY_PATH=$HOME/anaconda2/lib:$LD_LIBRARY_PATH swig
```

__NOTE:__ If you get errors in compilation, please contact for a patch.
It's a known issue that `swig` doesn't recognize `//` as comment.

## Contacts

Yuhuang Hu  
Email: duguyue100@gmail.com
