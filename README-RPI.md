# Build PyAER on Raspberry Pi

This is a working build instruction on Raspberry Pi 3B with Raspbian Stretch.

## Install dependencies

```bash
sudo apt-get install build-essential cmake pkg-config libusb-1.0-0-dev
sudo apt-get install automake bison libpcre3-dev
```

## Install `libcaer`

The `libcaer` can be installed as follows

```bash
git clone https://gitlab.com/inivation/dv/libcaer.git
cd libcaer
cmake -DCMAKE_INSTALL_PREFIX=/usr .
make -j4
sudo make install
```

## Install `swig`

You can compile `swig` with the following steps:

```bash
git clone https://github.com/duguyue100/swig
cd swig
./autogen.sh
# choose one of the configure settings
./configure --with-python=$(command -v python) --without-python2 --without-pcre  # for python 3
make -j4
sudo make install
```

## Compile `pyaer`

Compile `pyaer` with the following steps:

```bash
git clone https://github.com/duguyue100/pyaer
sudo make install
```

## Contacts

Yuhuang Hu  
Email: duguyue100@gmail.com
