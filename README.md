# Py-sonde-comparison

Python tool designed to allow for generic(ish) comparisons between WOUDC ozonesondes and multiple different satellite types.

Author: E Malina NASA/JPL/Caltech October 2022.

This program makes use of the WOUDC pywoudc package (https://github.com/woudc/pywoudc), to allow for easy pythonic access to the WOUDC datasets.

Please note that ingesting satellite data from different groups still requires changing, thoughts and advice on this is welcome.

## Initial Requirements

- Python 3 and above
- Virtualenv
- Git

If not already installed, recommend installing miniconda (https://docs.conda.io/en/latest/miniconda.html).

## First step - Install pywoudc

Pywoudc env is necessary in order to use Py-sonde-comparison. Pywoudc is available from (https://github.com/woudc/pywoudc), prior to installing, please ensure the following package is installed.

Python package requirements:

OWSLib 

Recommended method after confirmed presence of conda or miniconda: 

```
conda install -c conda-forge owslib
```

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



For all uses of Py-sonde-comparison, please ensure the pywoudc environment is active, by typing:

```
conda activate pywoudc 
```

in the terminal. 

## Second Step - Setup Py-sonde-comparison

### Clone repository

Create a directory where you want to store the code repository, e.g. 'pysonde'

```
mkdir -p pysonde
```

Switch to the `pysonde` dir:

```
cd pysonde
```

Clone the repository:

```
git clone https://github.com/NASA-TROPESS/py-sonde-comparison.git
cd py-sonde-comparison
```

Create a branch for yourself, to allow for development:

```
git fetch --all
git checkout main
git branch $USER
```

Switch to your branch:

```
git checkout $USER
```

Push your branch to GitHub:

```
git push
```

Verify.

> You should see a star (`*`) next to your username:

```
git branch
```



## Second Step - Using Py-sonde-comparison

Initialise the virtual environment with the following command:

```
source configure.sh
```

Your command line interface should look similar to this:

```
(.venv) (pywoudc) [ebmalina@tb14 py-sonde-comparison]$  
```

To see the code in py-sonde-comparison, it is all stored in the py_sonde_comparison folder. With cli.py forming the lion's share of the code. 

The code is split into two key components, 'colocate' and 'plot_results'. Colocate takes input satellite data and colocates the footprints with ozonesonde data within a certain date range. The output from colocate is an npz file, which the 'plot_results' function uses. Plot_results reads in the npz file and plots the data, currently only percentage column differences are plotted, but this can be adapted as needed depending on requirements.

colocate currently calls the function 'read_product' which is responsible for grabbing the necessary data from the satellite data products (date,latitude,longitude,ozone,ozone_apriori,aver_ker,pressure,hour). At the moment this only works with TROPESS data products, but working with the relevent satellite groups, this will be adapted to all relevent quirks of each satellite data product.  

The next step is to test/run the code. In the run directory are two example files:

cris_sonde_colocate.sh - This script runs the colocate for the TROPESS CrIS product, invoking takes this form in the this script.

```
  py-sonde-comparison colocate \
    --dataset TROPESS-CRIS \
    --start-date 2018-01-30 \
    --end-date 2018-06-30 \
    --input ~/output_py \
    --output ~/output_py/ozonesonde/ \
    --ozone-units 'None' \
    --gaw-locations 'all' \
    --distance-location 100 \
    --distance-time 3

```

Changable parameters are as follows:

--dataset: This specifies the source of the satellite data, this requires modification in the 'read_product' function anytime a new dataset is added. Plus in the line shown below, the click.Choice option, must be updated to reflect this change, so the new satellite product is a selectable choice.

```
@click.option('--dataset', '-ds', required=True, type=click.Choice(['TROPESS-CRIS'], case_sensitive=False),help='Indicate the source of the data in use.')
```

--start-date: Indicates the starting point of the comparison, must be in the format yyyy-mm-dd

--end-date: As start date, but indicating the end point of the comparison.

--input: Path of the L2 satellite ozone product files.

--output: Path to save the colocated npz files.

--ozone-units: Indicates the units of the ozone values in the satellite files, at the moment the script wants ozone values in ppb, and will convert the units as specified. However, new units will need to be added to the code, as needed.

--gaw-locations: Identifies which ozonesonde sites to compare against, standard is 'all', but can specify individual sites if required.

--distance-location: Specifies the maximum distance difference between satellite and sonde, set as 100km as standard, but can be any value desired.

--distance-time: Specifies the maximum time difference in hours between satellite retrieval and sonde. Standard is 3 hrs, but can be any time desired.

In order to execute this file, the following command can be invoked:

```
./run/cris_sonde_colocate.sh
```

This file can be changed/modified as required

cris_sonde_plot.sh - This script runs the plot_results for the output from colocate.

```
 py-sonde-comparison plot-results \
    --available-datasets TROPESS-CRIS,TROPESS-AIRSOMI \
    --input ~/output_py/ozonesonde/ \
    --output ~/output_py/ozonesonde/

```

--available-datasets: A comma seperated list of the datasets required for plotting, dataset names must be the same as those specified in the --dataset command in colocate.

--input: Path of the colocated npz datasets.

--output: Path for the plots generated from this routine. 
