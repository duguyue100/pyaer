# Install PyAER from Source


## Install `libcaer`

cd to your root software development folder. You will install libcaer to the system here.

```bash
  sudo apt-get update
  sudo apt-get install build-essential pkg-config libusb-1.0-0-dev
  git clone https://gitlab.com/inivation/dv/libcaer.git
  cd libcaer
  git checkout e68c3b4c115f59d5fd030fd44db12c702dddc3a5
  sudo apt install cmake
  cmake -DCMAKE_INSTALL_PREFIX=/usr .
  make -j
  sudo make install
  cd .. # go back to your root
  ```

__NOTE:__ For more information, see [`libcaer` repo](https://github.com/inilabs/libcaer).

## Install `swig`

This repository uses SWIG to create Python bindings. And you will need to
compile the latest SWIG from source. The reason is because current SWIG
cannot handle some cases in `libcaer`, we made a modified SWIG for this purpose.

You will install swig to the system here.

1. Install compilation dependency. From terminal

    ```
    sudo apt-get install automake
    sudo apt-get install bison
    ```

    _There might be other dependencies for compiling SWIG_

2. Compile SIWG. From terminal,

    ```bash
    git clone https://github.com/duguyue100/swig
    cd swig
    ./autogen.sh
    ./configure
    make
    sudo make install
   cd .. # go back up to your root
    ```

    Alternatively, for compiling SWIG with Python

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
cd to your root software development folder. You will clone pyaer here and then install to your system (or conda env) in developer mode, so that your environment uses your cloned code.
From terminal
```
git clone https://github.com/duguyue100/pyaer.git
cd pyaer
make develop
```
