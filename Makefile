
DESTDIR=/
PYTHON=python

prefix=/usr
bindir=$(prefix)/bin

install:
	cd pyportmidi
	$(PYTHON) setup.py install
	cd ..
	$(PYTHON) setup.py install
