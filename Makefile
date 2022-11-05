# This is a Python template Makefile, do modification as you want
#
# Project: PyAER
# Author: Yuhuang Hu
# Email : duguyue100@gmail.com

PYTHONPATH="$(shell printenv PYTHONPATH):$(PWD)"
PYTHONLIBPATH="$(shell python -c 'from sysconfig import get_paths; print(get_paths()["stdlib"]+"/..")')"
PYTHONLIBPATHWIN="$(shell python -c 'from sysconfig import get_paths; print(get_paths()["stdlib"]+"\..")')"

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

dvs128-test:
	python ./scripts/dvs128_test.py

edvs-test:
	python ./scripts/edvs_test.py

dvs128-thread-test:
	python ./scripts/dvs128_thread_test.py

dvs128-vispy:
	python ./scripts/dvs128_vispy.py

dvs128-glumpy:
	python ./scripts/dvs128_glumpy.py

davis240-test:
	python ./scripts/davis240_test.py

davis346-test:
	python ./scripts/davis346_test.py

davis346-color-test:
	python ./scripts/davis346_color_test.py

davis346-color-events:
	python ./scripts/davis346_color_events.py

dvxplorer-test:
	python ./scripts/dvxplorer_test.py

dvs-noise-filter-test:
	python ./scripts/dvs_noise_filter_test.py

device-discovery:
	python ./scripts/device_discovery.py

event-container-test:
	python ./scripts/event_container_test.py

install:
	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(PYTHONLIBPATH) python setup.py install

develop:
	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(PYTHONLIBPATH) python setup.py develop

develop-uninstall:
	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(PYTHONLIBPATH) python setup.py develop --uninstall

build-pyaer:
	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(PYTHONLIBPATH) python setup.py build

build-win:
	LD_LIBRARY_PATH=$(PYTHONLIBPATHWIN) python setup.py build -cmingw32

build-wheel:
	LD_LIBRARY_PATH=$(LD_LIBRARY_PATH):$(PYTHONLIBPATH) python setup.py bdist_wheel

cleanall:
