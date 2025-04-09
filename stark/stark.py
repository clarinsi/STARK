#!/usr/bin/env python
# Copyright 2019 CJVT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import configparser
import os
from pathlib import Path
import sys
import logging

from stark.data.representation.empty_namespace import EmptyNamespace
# from pympler import asizeof

from stark.data.summary import Summary
from stark.processing.filters import read_filters
from stark.processing.processor import Processor
from stark.processing.query_trees import generate_query_trees, get_query_tree_size_range
from stark.processing.writers import TSVWriter, ObjectWriter

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger('stark')

sys.setrecursionlimit(25000)


def parse_args(args):
    """
    Returns Namespace object containing given arguments.
    :param args:
    :return:
    """
    parser = argparse.ArgumentParser()

    # Required parameters
    parser.add_argument("--config_file", default=str(Path.joinpath(Path(__file__).parent.parent, "config.ini")), type=str,
                        help="The input config file.")
    parser.add_argument("--input", default=None, type=str, help="The input file/folder.")
    parser.add_argument("--output", default=None, type=str, help="The output file.")
    parser.add_argument("--internal_saves", default=None, type=str, help="Location for internal_saves.")
    parser.add_argument("--cpu_cores", default=None, type=int, help="Number of cores used.")
    parser.add_argument("--greedy_counter", default=None, type=str, help="Uses greedy counter.")

    parser.add_argument("--size", default=None, type=str, help="Size of trees displayed.")
    parser.add_argument("--processing_size", default=None, type=str, help="Limits the size of trees during processing.")
    parser.add_argument("--complete", default=None, type=str, help="Tree type.")
    parser.add_argument("--labeled", default=None, type=str, help="Dependency type.")
    parser.add_argument("--fixed", default=None, type=str, help="Order of node.")
    parser.add_argument("--node_type", default=None, type=str, help="Type of node.")

    parser.add_argument("--allowed_labels", default=None, type=str, help="Label not included here will not be counted.")
    parser.add_argument("--ignored_labels", default=None, type=str,
                        help="Labels that contain these parsing tags will be counted"
                             " but ignored in result representations.")
    parser.add_argument("--head", default=None, type=str, help="Head whitelist.")

    parser.add_argument("--query", default=None, type=str, help="Query.")

    # output settings
    parser.add_argument("--grew_match", default=None, type=str, help="Output setting for printing query and url.")
    parser.add_argument("--label_subtypes", default=None, type=str, help="Output setting for printing query and url.")
    parser.add_argument("--depsearch", default=None, type=str, help="Output setting for printing depsearch query.")
    parser.add_argument("--example", default=None, type=str, help="Print one example in a separate column.")
    parser.add_argument("--sentence_count_file", default=None, type=str,
                        help="Path to a file where counts of queries will be stored per sentence.")
    parser.add_argument("--detailed_results_file", default=None, type=str,
                        help="Path to a file where all examples will be stored.")
    parser.add_argument("--annodoc_example_dir", default=None, type=str,
                        help="Path to a directory where annodoc example files are stored (js library for visualization).")
    parser.add_argument("--annodoc_detailed_dir", default=None, type=str,
                        help="Path to a directory where annodoc detailed files are stored (js library for visualization).")

    parser.add_argument("--max_lines", default=None, type=int, help="Maximum number of trees in the output.")
    parser.add_argument("--node_info", default=None, type=str, help="Information about nodes in separate columns.")
    parser.add_argument("--head_info", default=None, type=str, help="Information about head in separate columns.")
    parser.add_argument("--frequency_threshold", default=None, type=int, help="Frequency threshold.")
    parser.add_argument("--association_measures", default=None, type=str, help="Association measures.")
    parser.add_argument("--continuation_processing", default=None, type=str, help="Nodes number.")
    parser.add_argument("--compare", default=None, type=str, help="Corpus with which we want to compare statistics.")
    return parser.parse_args(args)


def count_subtrees(configs, filters):
    """
    Counts subtrees that match filters.
    :param configs:
    :param filters:
    :return:
    """
    processor = Processor(configs, filters)
    summary = Summary()
    if not configs['greedy_counter'] or filters['tree_size_range'][0] == 0:
        summary.set_query_trees(generate_query_trees(configs, filters))

        # set min and max tree size to limit greedy generation
        if configs['greedy_counter']:
            filters['tree_size_range'] = get_query_tree_size_range(summary.query_trees)

    if os.path.isdir(configs['input_path']):
        summary = processor.run_dir(summary)

    else:
        summary = processor.run(configs['input_path'], summary)

    return summary


def read_configs(config, args=EmptyNamespace()):
    """
    Merges concrete settings from config files with arguments. When arguments are given, they override settings from
    configuration file. Look into documentation for which parameters in config file are required.
    :param config: ConfigParser object containing settings from configuration file.
    :param args: Namespace object containing given arguments.
    :return: Dictionary with configuration settings.
    """

    configs = {}
    # mandatory parameters
    configs['input_path'] = config.get('settings', 'input') if not args.input else args.input
    if config.has_option('settings', 'output') or args.output:
        configs['output'] = config.get('settings', 'output') if not args.output else args.output
    else:
        configs['output'] = None
    configs['display_size'] = config.get('settings', 'size', fallback='0') if not args.size else args.size
    configs['tree_size'] = config.get('settings', 'processing_size', fallback='0') if not args.processing_size else (
        args.processing_size)
    if config.has_option('settings', 'node_type') or args.node_type:
        configs['node_type'] = config.get('settings', 'node_type') if not args.node_type else args.node_type
    else:
        configs['node_type'] = None

    # mandatory parameters with default value
    configs['greedy_counter'] = (config.getboolean('settings', 'greedy_counter') if not args.greedy_counter
                                  else args.greedy_counter == 'yes')
    configs['internal_saves'] = (config.get('settings', 'internal_saves')
                                 if config.has_option('settings', 'internal_saves') else None) \
        if not args.internal_saves else args.internal_saves
    configs['cpu_cores'] = (config.getint('settings', 'cpu_cores') if config.has_option('settings', 'cpu_cores')
                            else 1) if not args.cpu_cores else args.cpu_cores
    configs['complete_tree_type'] = (config.getboolean('settings', 'complete') if not args.complete
                                     else args.complete == 'yes')
    configs['dependency_type'] = (config.getboolean('settings', 'labeled') if not args.labeled
                                  else args.labeled == 'yes')
    configs['node_order'] = (config.getboolean('settings', 'fixed') if not args.fixed else args.fixed == 'yes')
    configs['association_measures'] = (config.getboolean('settings', 'association_measures')
                                       if not args.association_measures else args.association_measures == 'yes')
    configs['node_info'] = (config.getboolean('settings', 'node_info')
                                       if not args.node_info else args.node_info == 'yes')
    configs['head_info'] = (config.getboolean('settings', 'head_info')
                            if not args.head_info else args.head_info == 'yes')

    # optional parameters
    if config.has_option('settings', 'allowed_labels') or args.allowed_labels:
        label_whitelist = config.get('settings',
                                     'allowed_labels') if not args.allowed_labels else args.allowed_labels
        configs['label_whitelist'] = label_whitelist.split('|')
    else:
        configs['label_whitelist'] = []

    if config.has_option('settings', 'ignored_labels') or args.ignored_labels:
        ignored_labels = config.get('settings', 'ignored_labels') if not args.ignored_labels else args.ignored_labels
        configs['ignored_labels'] = ignored_labels.split('|')
    else:
        configs['ignored_labels'] = []

    if config.has_option('settings', 'head') or args.head:
        root_whitelist = config.get('settings',
                                    'head') if not args.head else args.head
        configs['root_whitelist'] = root_whitelist.split('|')
    else:
        configs['root_whitelist'] = []

    if config.has_option('settings', 'query') or args.query:
        configs['query'] = (config.get('settings', 'query') if not args.query else args.query)
        # query has priority over the size, so we set it to 0
        configs['display_size'] = '0'
        configs['tree_size'] = '0'

    if args.compare:
        configs['compare'] = args.compare
    else:
        configs['compare'] = config.get('settings', 'compare') if config.has_option('settings', 'compare') else None

    configs['frequency_threshold'] = config.getfloat('settings', 'frequency_threshold', fallback=0) \
        if not args.frequency_threshold else args.frequency_threshold
    configs['lines_threshold'] = config.getint('settings', 'max_lines', fallback=0) \
        if not args.max_lines else args.max_lines

    configs['continuation_processing'] = config.getboolean('settings', 'continuation_processing', fallback=False) \
        if not args.continuation_processing else args.continuation_processing == 'yes'

    configs['grew_match'] = config.getboolean('settings',
                                              'grew_match') if not args.grew_match else args.grew_match == 'yes'
    configs['example'] = config.getboolean('settings', 'example') \
        if not args.example else args.example == 'yes'
    configs['label_subtypes'] = config.getboolean('settings', 'label_subtypes') \
        if not args.label_subtypes else args.label_subtypes == 'yes'

    if args.sentence_count_file:
        configs['sentence_count_file'] = args.sentence_count_file
    else:
        configs['sentence_count_file'] = config.get('settings', 'sentence_count_file') \
            if config.has_option('settings', 'sentence_count_file') else None

    if args.detailed_results_file:
        configs['detailed_results_file'] = args.detailed_results_file
    else:
        configs['detailed_results_file'] = config.get('settings', 'detailed_results_file') \
            if config.has_option('settings', 'detailed_results_file') else None

    if args.annodoc_example_dir:
        configs['annodoc_example_dir'] = args.annodoc_example_dir
    else:
        configs['annodoc_example_dir'] = config.get('settings', 'annodoc_example_dir') \
            if config.has_option('settings', 'annodoc_example_dir') else None

    if args.annodoc_detailed_dir:
        configs['annodoc_detailed_dir'] = args.annodoc_detailed_dir
    else:
        configs['annodoc_detailed_dir'] = config.get('settings', 'annodoc_detailed_dir') \
            if config.has_option('settings', 'annodoc_detailed_dir') else None

    configs['depsearch'] = config.getboolean('settings', 'depsearch') \
        if not args.depsearch else args.depsearch == 'yes'

    configs['nodes_number'] = True

    if configs['compare'] is not None:
        configs['other_input_path'] = configs['compare']

    # when processing_size is not given and display_size is set processing_size or throw an error!
    if configs['tree_size'] == '0' and configs['display_size'] != '0':
        if configs['complete_tree_type'] and configs['greedy_counter']:
            configs['tree_size'] = '1-10000000'
        else:
            raise ValueError('You have to specify `processing_size` parameter!')

    if configs['tree_size'] != '0' and configs['display_size'] == '0':
        raise ValueError('When `processing_size` setting is set, `size` has to be specified as well!')

    return configs


def read_settings(config_file, args=EmptyNamespace()):
    """
    Reads configuration file and merges it with arguments.
    :param config_file: path to config file.
    :param args: Namespace object
    :return:
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    return read_configs(config, args)


def run(configs):
    """
    Executes STARK processing.
    :param configs: Dictionary containing execution settings.
    :return: Either object with results or None, when results are stored into tsv file.
    """

    filters = read_filters(configs)
    summary = count_subtrees(configs, filters)

    other_summary = None
    if configs['compare'] is not None:
        configs['input_path'] = configs['other_input_path']
        other_summary = count_subtrees(configs, filters)
    if configs['output']:
        writer = TSVWriter(summary, other_summary, filters, configs)
    else:
        writer = ObjectWriter(summary, other_summary, filters, configs)
    return writer.write()
