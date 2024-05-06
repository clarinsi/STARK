import filecmp
import os
import random
import shutil

import pytest
import stark
from stark.stark import read_settings, parse_args
from tests import *


def test1():
    """
    Testing regular run.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config1.ini')
    settings = read_settings(config_file, parse_args([]))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_config1.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_config1.tsv'))


def test2():
    """
    Test compare.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config2.ini')
    settings = read_settings(config_file, parse_args([]))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_config2.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_config2.tsv'))


def test3():
    """
    Test complete=no and query.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config3.ini')
    settings = read_settings(config_file, parse_args([]))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_config3.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_config3.tsv'))
