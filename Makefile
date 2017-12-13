# This is a Python template Makefile, do modification as you want
#
# Project: PyAER
# Author: Yuhuang Hu
# Email : duguyue100@gmail.com

HOST = 127.0.0.1
PYTHONPATH="$(shell printenv PYTHONPATH):$(PWD)"
PYTHONLIBPATH="$(shell python -c 'from sysconfig import get_paths; print(get_paths()["stdlib"]+"/..")')"

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

run:

test:
	PYTHONPATH=$(PYTHONPATH) python

dvs128-test:
	PYTHONPATH=$(PYTHONPATH) python ./pyaer/scripts/dvs128_test.py

install:
	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(PYTHONLIBPATH) python setup.py install

build-pyaer:
	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(PYTHONLIBPATH) python setup.py build

cleanall:
