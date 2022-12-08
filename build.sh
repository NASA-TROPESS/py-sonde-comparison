#!/usr/bin/env bash

# see: https://www.python.org/dev/peps/pep-0441/

# get script dir
script_path=`dirname ${BASH_SOURCE[0]}`

pushd $script_path > /dev/null

# Build Python executable (PEX)
echo "Building Python executable bin/py-filter ..."

rm -rf .venv/* && \
source configure.sh

# use custom TMPDIR to avoid running out of space in /tmp
export TMPDIR=~/muses/tmp
mkdir -p $TMPDIR

mkdir -p bin && \
pex . \
    --tmpdir $TMPDIR \
    --resolver-version pip-2020-resolver \
    --python-shebang "/usr/bin/env python3.8" \
    --requirement py_sonde_configure/requirements.txt \
    --script=Py-sonde-configure \
    --output-file bin/Py-sonde-configure 

deactivate

export TMPDIR=

popd > /dev/null