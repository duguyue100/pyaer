# Customize Building Process

This folder contains a compile script that performs
customized build for pyaer.
We replaced this version of build to a easier building process.
This script is here for the legacy reasons.


## Some old logs

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
