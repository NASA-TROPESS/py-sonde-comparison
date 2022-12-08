#!/usr/bin/env bash

# allow others to write to .venv
umask 0

# C Libraries

# this is needed by the pyhdf package
if [[ "$CONDA_DEFAULT_ENV" ]]; then
    export CPPFLAGS="-I${CONDA_PREFIX}/include"
    export LDFLAGS="-L${CONDA_PREFIX}/lib"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    export CPPFLAGS="-I/usr/include"
    export LDFLAGS="-L/usr/lib64/hdf"   
fi

# Python

# Install Python if not in conda environment and not in DOCKER
if [[ -z "$CONDA_DEFAULT_ENV" && ! -f /.dockerenv ]]
then
    # install Python 3.8.9 if not installed
    pyenv install 3.8.9 --skip-existing
    pyenv versions

    # use Python 3 from .python-version for local development
    eval "$(pyenv init --path)"
fi

# use custom TMPDIR to avoid running out of space in /tmp
export TMPDIR=~/muses/tmp
mkdir -p $TMPDIR

# create virtual environment
python3 -m venv .venv

# activate virtual environment
source .venv/bin/activate

if [[ "$1" != "quick" ]] ; then
    # change permissions of .venv
    chmod -R 777 .venv

    # upgrade pip
    pip install --upgrade pip wheel

    # install development packages
    pip install -r dev/requirements.txt

    # not needed because pip install --editable . will run setup.py
    # install runtime packages
    # pip install -r py_filter/requirements.txt

    # install our package for easy development
    # will use requirements from setup.py
    pip install --editable .
fi

export TMPDIR=
