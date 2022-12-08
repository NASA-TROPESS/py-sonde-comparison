# Examples

Configure the project before running:

```bash
source configure.sh
```

## CrIS

### Train 

Input radiances will be read from the `~/output/cris/{date}/combine/World` directories:

```bash
py-filter train \
  --sensor-set CrIS \
  --species CO,H2O,TATM \
  --start-date 2016-08-18 \
  --end-date 2016-08-18 \
  --profile World \
  --input ~/output/cris \
  --output ~/output/models/filter/cris/2016-08-18_2016-08-18
```

### Predict

Output will be saved to the `~/output/cris/2016-08-18/filter/World` directory:

```bash
py-filter predict \
  --sensor-set CrIS \
  --species CO,H2O,TATM \
  --models ~/output/models/filter/cris/2016-08-18_2016-08-18 \
  --input ~/output/cris/2016-08-18/geolocate/World \
  --output ~/output/cris/2016-08-18/filter/World
```

## CrIS-JPSS-1

### Train 

Input radiances will be read from the `~/output/cris_jpss_1/{date}/combine/World` directories:

```bash
py-filter train \
  --sensor-set CrIS-JPSS-1 \
  --species CO,H2O,TATM \
  --start-date 2018-08-18 \
  --end-date 2018-08-18 \
  --profile World \
  --input ~/output/cris_jpss_1 \
  --output ~/output/models/filter/cris_jpss_1/2018-08-18_2018-08-18
```

### Predict

Output will be saved to the `~/output/cris_jpss_1/2018-08-18/filter/World` directory:

```bash
py-filter predict \
  --sensor-set CrIS-JPSS-1 \
  --species CO,H2O,TATM \
  --models ~/output/models/filter/cris_jpss_1/2018-08-18_2018-08-18 \
  --input ~/output/cris_jpss_1/2018-08-18/geolocate/World \
  --output ~/output/cris_jpss_1/2018-08-18/filter/World
```

