import shutil

from pathlib import Path
from click.testing import CliRunner
from py_filter.cli import cli


def cris_train():
    #input_dir = Path('~/output/cris').expanduser().resolve()
    
    output_dir = Path('~/output_py/models/filter/cris-jpss-1').expanduser().resolve()

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    runner = CliRunner()
    result = runner.invoke(cli, [
        'train',
        '--sensor-set', 'cris-jpss-1',
        '--species', 'O3',
        '--date', '2022-06-01',
        '--output', output_dir
    ])

    print(result.output)


def cris_predict():
#    model_dir = Path('~/OSP/ML_Filter/models/').expanduser().resolve()
    model_dir = Path('~/RetrievalFailure/update_results/PCA/').expanduser().resolve()

    input_dir = Path('~/output_py/cris/2020-08-12/thin/Global_Survey_Grid_0.8').expanduser().resolve()
    output_dir = Path('~/output_py/cris/2020-08-12/thin/Global_Survey_test').expanduser().resolve()

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    runner = CliRunner()
    result = runner.invoke(cli, [
        'predict',
        '--sensor-set', 'CrIS',
        '--date', '2020-08-12',
        '--species', 'O3',
        '--profile', 'Global_Survey_Grid_0.8',
        '--input-type', 'Thin',
        '--models', model_dir,
        '--input', input_dir,
        '--output', output_dir,
        '--threshold', 0.5
        #'--window'
    ])

    print(result.output)


if __name__ == "__main__":
    # executes only if run as a script
    pass

    #cris_train()
    cris_predict()
