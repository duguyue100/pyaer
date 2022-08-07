# Install PyAER from Source

## Install `libcaer`

```bash
# for Ubuntu
sudo apt-get install libcaer-dev
# for macOS
brew install libcaer
```

## Install `swig`

This repository uses SWIG to create Python bindings. And you will need to
compile the latest SWIG from source. The reason is because current SWIG
cannot handle some cases in `libcaer`, we made a modified SWIG for this purpose.

1. Install compilation dependency

    ```bash
    sudo apt-get install automake
    sudo apt-get install bison
    ```

    _There might be other dependencies for compiling SWIG_.

2. Compile SIWG

    ```bash
    git clone https://github.com/duguyue100/swig
    cd swig
    ./autogen.sh
    ./configure
    # For compiling SWIG with Python
    ./configure --without-alllang --with-python=$(command -v python)
    make -j4
    sudo make install
    ```

    __NOTE:__ For ARM-based Linux, you may also add `--without-pcre` to ignore the error during compilation.

    __NOTE:__ If you are not compile the SWIG with system Python distribution,
    it won't link to the custom Python automatically.

    You will need to configure `LD_LIBRARY_PATH` for swig running properly, i.e.,

    ```bash
    LD_LIBRARY_PATH=$HOME/miniconda/lib:$LD_LIBRARY_PATH swig
    ```

## Build `pyaer` from source

```bash
git clone https://github.com/duguyue100/pyaer.git
cd pyaer
make develop
```
