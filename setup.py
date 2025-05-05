import re
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# read the version from classla/_version.py
version_file_contents = open(path.join(here, 'stark/_version.py'), encoding='utf-8').read()
VERSION = re.compile('__stark_version__ = \'(.*)\'').search(version_file_contents).group(1)

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()

long_description = re.sub(
    r'\[([^\]]+)\]\((?!http)([^)]+)\)',
    r'[\1](https://github.com/clarinsi/STARK/blob/master/\2)',
    long_description
)

setup(name='stark-trees',
  version=VERSION,
  description=u"Parser for dependency trees",
  long_description=long_description,
  long_description_content_type="text/markdown",
  author='CLARIN.SI',
  author_email='info@clarin.si',
  # The project's main homepage.
  url='https://github.com/clarinsi/STARK.git',
  license='Apache 2.0',
  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    'pyconll>=3.1.0',
    'networkx>=3.3',
    'tqdm>=4.66.4'
  ],
  entry_points={
      "console_scripts": [
      "stark=stark.cli:main",  # This maps `stark` to `stark.cli.main()`
    ],
  },
  # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
  classifiers=[
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      'Development Status :: 4 - Beta',

      # Indicate who your project is intended for
      'Intended Audience :: Developers',
      'Intended Audience :: Education',
      'Intended Audience :: Science/Research',
      'Intended Audience :: Information Technology',
      'Topic :: Scientific/Engineering',
      'Topic :: Scientific/Engineering :: Information Analysis',
      'Topic :: Text Processing',
      'Topic :: Text Processing :: Filters',
      'Topic :: Text Processing :: Linguistic',
      'Topic :: Software Development',
      'Topic :: Software Development :: Libraries',

      # Specify the Python versions you support here. In particular, ensure
      # that you indicate whether you support Python 2, Python 3 or both.
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Programming Language :: Python :: 3.8',
      'Programming Language :: Python :: 3.9',
      'Programming Language :: Python :: 3.10',
  ],
  python_requires='>=3.6',
  # What does your project relate to?
  keywords='universal-dependencies dependency-parsing dependency-trees subtree-extraction treebank syntactic-analysis corpus-linguistics computational-linguistics text-analysis syntax extraction comparison natural-language-processing nlp natural-language-understanding clarinsi',

)
