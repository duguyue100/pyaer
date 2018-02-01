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
	python ./scripts/dvs128_test.py

dvs128-thread-test:
	python ./scripts/dvs128_thread_test.py

davis240-test:
	python ./scripts/davis240_test.py

davis346-test:
	python ./scripts/davis346_test.py

dynapse-test:
	python ./scripts/dynapse_test.py

install:
	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(PYTHONLIBPATH) python setup.py install

build-pyaer:
	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(PYTHONLIBPATH) python setup.py build

build-wheel:
	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(PYTHONLIBPATH) python setup.py bdist_wheel

cleanall:
