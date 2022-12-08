#!/usr/bin/env bash

# switch to ..
script_path=`dirname ${BASH_SOURCE[0]}`
pushd $script_path/..

# everything is awesome
umask 0

# create or clear output directory
#mkdir -p ~/output_py/ozonesonde
#rm -rf ~/output_py/ozonesonde/*

# run py-sonde-comparison
time \
  py-sonde-comparison plot-results \
    --available-datasets TROPESS-CRIS,TROPESS-AIRSOMI \
    --input ~/output_py/ozonesonde/ \
    --output ~/output_py/ozonesonde/

    
popd
