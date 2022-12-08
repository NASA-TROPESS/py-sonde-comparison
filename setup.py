from setuptools import setup

setup(name='py_sonde_comparison',
      version='0.1.0',
      description='Satellite, ozonesonde comparison tool, will largely be generic to allow for multiple satellite datasets',
      url='https://github.jpl.nasa.gov/MUSES-Processing/Py-sonde-comparison',
      license='MIT',
      packages=['py_sonde_comparison'],
      scripts=['shell/Py-sonde-comparison'],
      install_requires=[
        'setuptools',
        'click==8.1.2',
        'numpy==1.22.0',
        'netCDF4==1.5.8',
        'xarray==2022.3.0',
        'matplotlib==3.5.1',
        'h5netcdf==1.0.0',
        'seaborn==0.12.0',
        'scipy==1.8.0',
        'pywoudc==0.2.0'
      ],
      zip_safe=False)
