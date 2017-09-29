# PyAER-beta

PyAER with Swig Bindings

Special thanks to [iniLabs](http://inilabs.com/) to make this possible.

Supported platform: `Ubuntu`

## Installation

1. Compile the most recent version of SWIG:

Install compilation dependency

```
$ sudo apt-get install automake
$ sudo apt-get install bison
```

_There might be other dependencies for compiling SWIG_

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

2. Download this repo

```
$ git clone --recursive https://github.com/duguyue100/pyaer-beta.git
```

3. Make this repository

```
$ ./compile make
```

4. (Optional) if you want to clean the installation, just type

```
$ ./compile clean
```

## Contacts

Yuhuang Hu  
Email: duguyue100@gmail.com
