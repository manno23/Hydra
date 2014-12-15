
DESTDIR=/
PYTHON=python

prefix=/usr
bindir=$(prefix)/bin

all:
	cd pyportmidi
	$(PYTHON) setup.py build
	cd ..
	$(PYTHON) setup.py build
	
install:
	cd pyportmidi
	$(PYTHON) setup.py install
	cd ..
	$(PYTHON) setup.py install
