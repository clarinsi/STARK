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
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    config_file = os.path.join(CONFIGS_DIR, 'config_base.ini')
    settings = read_settings(config_file, parse_args([]))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_base.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_base.tsv'))


def test_greedy_complete():
    """
    Testing regular run.
    :return:
    """
    random.seed(12)
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    config_file = os.path.join(CONFIGS_DIR, 'config_greedy_complete.ini')
    settings = read_settings(config_file, parse_args([]))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_greedy_complete.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_greedy_complete.tsv'))


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
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_compare.ini')
    settings = read_settings(config_file, parse_args(['--greedy_counter', 'yes']))
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

    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_query.ini')
    settings = read_settings(config_file, parse_args(['--greedy_counter', 'yes']))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_query.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_query.tsv'))


def test_fixed():
    """
    Test complete=no and query.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_base.ini')
    settings = read_settings(config_file, parse_args(['--fixed', 'no',
                                                      '--output', 'test_data/output/out_fixed.tsv']))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_fixed.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_fixed.tsv'))

    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_base.ini')
    settings = read_settings(config_file, parse_args(['--greedy_counter', 'yes',
                                                      '--fixed', 'no',
                                                      '--output', 'test_data/output/out_fixed.tsv']))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_fixed.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_fixed.tsv'))


def test_dir():
    """
    Test complete=no and query.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_base.ini')
    settings = read_settings(config_file, parse_args(['--input', 'test_data/input/dir_input/',
                                                      '--output', 'test_data/output/out_dir.tsv']))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_dir.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_dir.tsv'))
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_base.ini')
    settings = read_settings(config_file, parse_args(['--input', 'test_data/input/dir_input/',
                                                      '--output', 'test_data/output/out_dir.tsv',
                                                      '--greedy_counter', 'yes']))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_dir.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_dir.tsv'))


def test_internal_storage():
    """
    Test internal storage.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_internal_storage.ini')
    output_mapper_dir = 'test_data/output/internal_saves'
    if os.path.exists(output_mapper_dir):
        shutil.rmtree(output_mapper_dir)
    settings = read_settings(config_file, parse_args([]))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_dir.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_dir.tsv'))

    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_internal_storage.ini')
    output_mapper_dir = 'test_data/output/internal_saves'
    if os.path.exists(output_mapper_dir):
        shutil.rmtree(output_mapper_dir)
    settings = read_settings(config_file, parse_args(['--greedy_counter', 'yes']))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_dir.tsv'), os.path.join(CORRECT_OUTPUT_DIR, 'out_dir.tsv'))


def test_internal_storage2():
    """
    Test internal storage.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_base.ini')
    output_mapper_dir = 'test_data/output/internal_saves'
    if os.path.exists(output_mapper_dir):
        shutil.rmtree(output_mapper_dir)
    settings = read_settings(config_file, parse_args(['--internal_saves', 'test_data/output/internal_saves',
                                                      '--output', 'test_data/output/out_internal_storage2.tsv']))
    stark.run(settings)
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_internal_storage2.tsv'), os.path.join(CORRECT_OUTPUT_DIR,
                                                                                           'out_internal_storage2.tsv'))

    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_base.ini')
    output_mapper_dir = 'test_data/output/internal_saves'
    if os.path.exists(output_mapper_dir):
        shutil.rmtree(output_mapper_dir)
    settings = read_settings(config_file, parse_args(['--internal_saves', 'test_data/output/internal_saves',
                                                      '--output', 'test_data/output/out_internal_storage2.tsv',
                                                      '--greedy_counter', 'yes']))
    stark.run(settings)
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_internal_storage2.tsv'), os.path.join(CORRECT_OUTPUT_DIR,
                                                                                           'out_internal_storage2.tsv'))


def test_output_settings():
    """
    Test complete=no and query.
    :return:
    """
    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_output_settings.ini')
    settings = read_settings(config_file, parse_args(['--detailed_results_file', 'test_data/output/detailed_results_file_query.tsv']))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_output_settings.tsv'), os.path.join(CORRECT_OUTPUT_DIR,
                                                                                         'out_output_settings.tsv'))
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'detailed_results_file_query.tsv'), os.path.join(CORRECT_OUTPUT_DIR,
                                                                                           'detailed_results_file_query.tsv'))
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'sentence_count_file.tsv'), os.path.join(CORRECT_OUTPUT_DIR,
                                                                                         'sentence_count_file.tsv'))

    random.seed(12)
    config_file = os.path.join(CONFIGS_DIR, 'config_output_settings.ini')
    settings = read_settings(config_file, parse_args(['--detailed_results_file',
                                                      'test_data/output/detailed_results_file_greedy.tsv',
                                                      '--sentence_count_file',
                                                      'test_data/output/sentence_count_file_greedy.tsv',
                                                      '--greedy_counter', 'yes']))
    stark.run(settings)
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'out_output_settings.tsv'), os.path.join(CORRECT_OUTPUT_DIR,
                                                                                         'out_output_settings.tsv'))
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'detailed_results_file_greedy.tsv'), os.path.join(CORRECT_OUTPUT_DIR,
                                                                                           'detailed_results_file_greedy.tsv'))
    assert filecmp.cmp(os.path.join(OUTPUT_DIR, 'sentence_count_file_greedy.tsv'), os.path.join(CORRECT_OUTPUT_DIR,
                                                                                         'sentence_count_file_greedy.tsv'))
