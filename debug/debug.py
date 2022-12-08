# For glob pattern usage see: 
# https://en.wikipedia.org/wiki/Glob_(programming)
# https://docs.python.org/3/library/glob.html

import shutil

from pathlib import Path
from click.testing import CliRunner
from py_filter.cli import cli


def cris_train():
    input_dir = Path('~/output/cris').expanduser().resolve()
    output_dir = Path('~/output/models/filter/cris/2016-08-18_2016-08-18').expanduser().resolve()

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    runner = CliRunner()
    result = runner.invoke(cli, [
        'train',
        '--sensor-set', 'CrIS',
        '--species', 'CO,H2O,TATM',
        '--start-date', '2016-08-18',
        '--end-date', '2016-08-18',
        '--profile', 'World',
        '--input', input_dir,
        '--output', output_dir
    ])

    print(result.output)


def cris_predict():
    model_dir = Path('~/output/models/filter/cris/2016-08-18_2016-08-18').expanduser().resolve()
    input_dir = Path('~/output/cris/2016-08-18/geolocate/World').expanduser().resolve()
    output_dir = Path('~/output/cris/2016-08-18/filter/World').expanduser().resolve()

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    runner = CliRunner()
    result = runner.invoke(cli, [
        'predict',
        '--sensor-set', 'CrIS',
        '--species', 'CO,H2O,TATM',
        '--models', model_dir,
        '--input', input_dir,
        '--output', output_dir
    ])

    print(result.output)


if __name__ == "__main__":
    # executes only if run as a script
    pass

    # cris_train()
    cris_predict()
