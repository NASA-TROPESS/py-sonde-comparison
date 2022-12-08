# Py-sonde-comparison

Python tool designed to allow for generic comparisons between WOUDC ozonesondes and multiple different satellite types.

Author: E Malina NASA/JPL/Caltech October 2022.

This program makes use of the WOUDC pywoudc package (https://github.com/woudc/pywoudc), to allow for easy pythonic access to the WOUDC datasets.

## Initial Requirements

- Python 3 and above
- Virtualenv
- Git

If not already installed, recommend installing miniconda (https://docs.conda.io/en/latest/miniconda.html).

## First step - Install pywoudc

Pywoudc env is necessary in order to use Py-sonde-comparison, from  (https://github.com/woudc/pywoudc).

Python package requirements:

OWSLib 

Recommended instillation method: conda install -c conda-forge owslib

Following installing owslib, please following the instruction below to setup a pywoudc environment in a terminal.

```
# setup virtualenv
python3 -m venv --system-site-packages pywoudc
cd pywoudc
source bin/activate

# clone codebase and install
git clone https://github.com/woudc/pywoudc.git
cd pywoudc
python setup.py build
python setup.py install
```



For all future uses of Py-sonde-comparison, please ensure the pywoudc environment is active, by typing "conda activate pywoudc" in the terminal.

## Second Step - Setup Py-sonde-comparison





## Examples

See [Examples](./docs/examples.md)

