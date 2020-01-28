#!/bin/bash
set -e
cd "$(dirname "$0")"
CONFIGDIR="config"
[ -d "$CONFIGDIR/plugins" ] || mkdir -p "$CONFIGDIR/plugins"
TEMP="$(mktemp -d)"
export PYTHONPATH="$TEMP"
python setup.py build develop --install-dir "$TEMP"
cp "$TEMP"/ShowMagnet.egg-link "$CONFIGDIR/plugins"

echo "deluge-gtk -c $CONFIGDIR"
