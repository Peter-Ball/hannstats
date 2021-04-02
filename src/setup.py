from distutils.core import setup, find_packages

setup(name='hannstats', 
      version='0.1.0',
      packages=findpackages(include=['hannstats']),
      description='support library for hannstats video project',
      author='Peter Ball',
      license='MIT')
