#!/bin/bash
set -e
CONFIGDIR="$(realpath config)"
cd /home/nitz/projects/deluge/showmagnet
mkdir temp
export PYTHONPATH=./temp
/usr/bin/python setup.py build develop --install-dir ./temp
pwd
cp ./temp/ShowMagnet.egg-link "$CONFIGDIR/plugins/"
rm -fr ./temp
