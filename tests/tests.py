import filecmp
import os
import random
import shutil

import pytest
import stark
from stark.stark import read_settings, parse_args
from tests import *


def test_base():
    """
    Testing regular run.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_base.ini')
    settings = read_settings(config_file, parse_args([]))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_base.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_base.tsv'))


def test_compare():
    """
    Test compare.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_compare.ini')
    settings = read_settings(config_file, parse_args([]))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_compare.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_compare.tsv'))


def test_query():
    """
    Test complete=no and query.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_query.ini')
    settings = read_settings(config_file, parse_args([]))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_query.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_query.tsv'))

def test_dir():
    """
    Test complete=no and query.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_base.ini')
    settings = read_settings(config_file, parse_args(['--input', 'test_data/input/',
                                                      '--output', 'test_data/output/out_dir.tsv']))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_dir.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_dir.tsv'))
