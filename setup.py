import re
from os import path
import os

from setuptools import setup, find_packages, Extension

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
    'networkx>=3.3',
    'tqdm>=4.66.4'
  ],
  ext_modules = [
      Extension(
          name="_stark",
          sources=[os.sep.join(["stark", "src", "_starkmodule.c"])],
          include_dirs=[],
          define_macros=[],
          library_dirs=[],
          libraries=[],
          extra_compile_args=["-Wall", "-Wextra", "-std=c99", "-pedantic",
          "-Werror", "-DNDEBUG"]
      )
  ]
)

