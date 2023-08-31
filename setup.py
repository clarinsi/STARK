import re
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# read the version from classla/_version.py
version_file_contents = open(path.join(here, 'stark/_version.py'), encoding='utf-8').read()
VERSION = re.compile('__stark_version__ = \'(.*)\'').search(version_file_contents).group(1)

setup(name='stark',
  version=VERSION,
  description=u"Parser for dependency trees",
  author='CLARIN.SI',
  author_email='info@clarin.si',
  license='Apache 2.0',
  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    'pyconll>=3.1.0',
  ],
)