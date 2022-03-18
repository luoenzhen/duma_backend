#!/bin/sh

# fail on first error
set -e

# this script is meant to run inside container with current working dir
# where source code is mounted.
apk add git make

pip install .[docs]

cd docs 
make "$@"
