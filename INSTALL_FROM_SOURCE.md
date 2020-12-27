# Install PyAER from Source

## Install `libcaer`

```bash
$ bash <(curl -s https://raw.githubusercontent.com/duguyue100/pyaer/master/install-libcaer.sh)
```

__NOTE:__ For more information, see [`libcaer` repo](https://github.com/inilabs/libcaer).

## Install `swig`

This repository uses SWIG to create Python bindings. And you will need to
compile the latest SWIG from source. The reason is because current SWIG
cannot handle some cases in `libcaer`, we made a modified SWIG for this purpose.

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

    __NOTE:__ For ARM-based Linux, you may also add `--without-pcre` to ignore the error during compilation.

    __NOTE:__ If you are not compile the SWIG with system Python distribution,
    it won't link to the custom Python automatically.

    You will need to configure `LD_LIBRARY_PATH` for swig running properly.

    i.e.

    ```
    LD_LIBRARY_PATH=$HOME/anaconda2/lib:$LD_LIBRARY_PATH swig
    ```

## Build `pyaer` from source

```
$ git clone https://github.com/duguyue100/pyaer.git
$ cd pyaer
$ make develop
```
