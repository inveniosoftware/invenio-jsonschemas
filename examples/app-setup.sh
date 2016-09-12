#!/bin/sh

# quit on errors:
set -o errexit

# quit on unbound symbols:
set -o nounset

DIR=`dirname $0`

# install the sample application
cd $DIR/samplepkg
pip install -e .
cd -
