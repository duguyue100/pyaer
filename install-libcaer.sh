#!/bin/bash

LIBCAER_TAG=88a8f54684ca0626ed4caa50a1f20414597bab18
TRAVIS_BUILD=false
# TODO: To support
LIBSERIAL_PORT_OPTION=false

# parse option
if [ ! -z "$1" -a "$1" = "travis" ]; then
    echo "[MESSAGE] This is a Travis build."
    TRAVIS_BUILD=true
elif [ ! -z "$1" -a "$1" = "libserial" ]; then
    echo "[MESSAGE] Enable libserial."
    LIBSERIAL_PORT_OPTION=true
elif [ ! -z "$1" -a "$1" = "travis.libserial" ]; then
    echo "[MESSAGE] This is a Travis build and enable libserial."
    TRAVIS_BUILD=true
    LIBSERIAL_PORT_OPTION=true
fi

case "$(uname -s)" in
    Darwin)
        echo 'Installing libcaer to a macOS'
        if [ $TRAVIS_BUILD = false ]; then
            brew install cmake pkg-config libusb
            git clone https://github.com/inivation/libcaer /tmp/libcaer
            cd /tmp/libcaer
        else
            git clone https://github.com/inivation/libcaer
            cd libcaer
        fi
        git checkout ${LIBCAER_TAG}
        cmake -DCMAKE_INSTALL_PREFIX=/usr/local .
        make -j2
        sudo make install
    ;;

    Linux)
        echo 'Installing libcaer to a Debian platform'
        if [ $TRAVIS_BUILD = false ]; then
            sudo apt-get update
            sudo apt-get install build-essential cmake pkg-config libusb-1.0-0-dev
            git clone https://github.com/inivation/libcaer /tmp/libcaer
            cd /tmp/libcaer
        else
            git clone https://github.com/inivation/libcaer
            cd libcaer
        fi
        git checkout ${LIBCAER_TAG}
        cmake -DCMAKE_INSTALL_PREFIX=/usr .
        make -j2
        sudo make install
    ;;

    CYGWIN*|MINGW32*|MSYS*)
        echo 'Installing libcaer to MS Windows'
    ;;

    *)
        echo 'other OS'
    ;;
esac
