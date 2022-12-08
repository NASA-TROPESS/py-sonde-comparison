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
  Py-sonde-comparison colocate \
    --dataset TROPESS-CRIS \
    --start-date 2018-01-30 \
    --end-date 2018-06-30 \
    --input ~/output_py \
    --output ~/output_py/ozonesonde/ \
    --ozone-units 'None' \
    --gaw-locations 'all' \
    --distance-location 100 \
    --distance-time 3 

    
popd
