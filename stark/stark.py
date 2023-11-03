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
import copy
import csv
import hashlib
import json
import math
import os
import pickle
import re
import string
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path
import gzip
import sys
import pyconll

from os import path
here = path.abspath(path.dirname(__file__))

from stark.generic import get_collocabilities, create_output_string_form, create_output_string_deprel, create_output_string_lemma, create_output_string_upos, create_output_string_xpos, create_output_string_feats
import urllib.parse

from stark.Tree import Tree

sys.setrecursionlimit(25000)


def save_zipped_pickle(obj, filename, protocol=-1):
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(filename, 'wb') as f:
        pickle.dump(obj, f, protocol)


def load_zipped_pickle(filename):
    with gzip.open(filename, 'rb') as f:
        loaded_object = pickle.load(f)
        return loaded_object


def decode_query(orig_query, dependency_type, feats_detailed_list):
    new_query = False

    # if command in bracelets remove them and treat command as new query
    if orig_query[0] == '(' and orig_query[-1] == ')':
        new_query = True
        orig_query = orig_query[1:-1]

    if dependency_type != '':
        decoded_query = {'deprel': dependency_type}
    else:
        decoded_query = {}

    if orig_query == '_':
        return decoded_query
    # if no spaces in query then this is query node and do this otherwise further split query
    elif len(orig_query.split(' ')) == 1:
        orig_query_split_parts = orig_query.split(' ')[0].split('&')
        for orig_query_split_part in orig_query_split_parts:
            orig_query_split = orig_query_split_part.split('=', 1)
            if len(orig_query_split) > 1:
                if orig_query_split[0] == 'L':
                    decoded_query['lemma'] = orig_query_split[1]
                elif orig_query_split[0] == 'upos':
                    decoded_query['upos'] = orig_query_split[1]
                elif orig_query_split[0] == 'xpos':
                    decoded_query['xpos'] = orig_query_split[1]
                elif orig_query_split[0] == 'form':
                    decoded_query['form'] = orig_query_split[1]
                elif orig_query_split[0] == 'feats':
                    decoded_query['feats'] = orig_query_split[1]
                elif orig_query_split[0] in feats_detailed_list:
                    decoded_query['feats_detailed'] = {}
                    decoded_query['feats_detailed'][orig_query_split[0]] = orig_query_split[1]
                    return decoded_query
                elif not new_query:
                    raise Exception('Not supported yet!')
                else:
                    print('???')
            elif not new_query:
                decoded_query['form'] = orig_query_split_part
        return decoded_query

    # split over spaces if not inside braces
    all_orders = re.split(r"\s+(?=[^()]*(?:\(|$))", orig_query)

    node_actions = all_orders[::2]
    priority_actions = all_orders[1::2]
    priority_actions_beginnings = [a[0] for a in priority_actions]

    # find root index
    try:
        root_index = priority_actions_beginnings.index('>')
    except ValueError:
        root_index = len(priority_actions)

    children = []
    root = None
    for i, node_action in enumerate(node_actions):
        if i < root_index:
            children.append(decode_query(node_action, priority_actions[i][1:], feats_detailed_list))
        elif i > root_index:
            children.append(decode_query(node_action, priority_actions[i - 1][1:], feats_detailed_list))
        else:
            root = decode_query(node_action, dependency_type, feats_detailed_list)
    if children:
        root["children"] = children
    return root


def create_trees(input_path, internal_saves, feats_detailed_dict={}, save=True):
    hash_object = hashlib.sha1(input_path.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    trees_read_outputfile = os.path.join(internal_saves, hex_dig) if internal_saves is not None else None
    print(Path(input_path).name)
    if trees_read_outputfile is None or not os.path.exists(trees_read_outputfile) or not save:

        train = pyconll.load_from_file(input_path)

        form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, feats_dict = {}, {}, {}, {}, {}, {}

        all_trees = []
        corpus_size = 0

        for sentence in train:
            root = None
            token_nodes = []
            for token in sentence:
                if not token.id.isdigit():
                    continue

                # TODO check if 5th place is always there for feats
                token_form = token.form if token.form is not None else '_'
                node = Tree(int(token.id), token_form, token.lemma, token.upos, token.xpos, token.deprel, token.feats, form_dict,
                            lemma_dict, upos_dict, xpos_dict, deprel_dict, feats_dict, feats_detailed_dict, token.head)
                token_nodes.append(node)
                if token.deprel == 'root':
                    root = node

                corpus_size += 1

            for token_id, token in enumerate(token_nodes):
                if isinstance(token.parent, int) or token.parent == '':
                    root = None
                    print('No parent: ' + sentence.id)
                    break
                if int(token.parent) == 0:
                    token.set_parent(None)
                else:
                    parent_id = int(token.parent) - 1
                    if token_nodes[parent_id].children_split == -1 and token_id > parent_id:
                        token_nodes[parent_id].children_split = len(token_nodes[parent_id].children)
                    token_nodes[parent_id].add_child(token)
                    token.set_parent(token_nodes[parent_id])

            for token in token_nodes:
                if token.children_split == -1:
                    token.children_split = len(token.children)

            if root == None:
                print('No root: ' + sentence.id)
                continue
            all_trees.append(root)

        if trees_read_outputfile is not None and save:
            save_zipped_pickle((all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, corpus_size, feats_detailed_dict), trees_read_outputfile, protocol=2)
    else:
        print('Reading trees:')
        print('Completed')
        all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, corpus_size, feats_detailed_dict = load_zipped_pickle(trees_read_outputfile)

    return all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, corpus_size, feats_detailed_dict


def printable_answers(query):
    # all_orders = re.findall(r"(?:[^ ()]|\([^]*\))+", query)
    all_orders = re.split(r"\s+(?=[^()]*(?:\(|$))", query)

    # all_orders = orig_query.split()
    node_actions = all_orders[::2]
    # priority_actions = all_orders[1::2]

    if len(node_actions) > 1:
        res = []
        # for node_action in node_actions[:-1]:
        #     res.extend(printable_answers(node_action[1:-1]))
        # res.extend([node_actions[-1]])
        for node_action in node_actions:
            # if command in bracelets remove them and treat command as new query
            # TODO FIX BRACELETS IN A BETTER WAY
            if not node_action:
                res.extend(['('])
            elif node_action[0] == '(' and node_action[-1] == ')':
                res.extend(printable_answers(node_action[1:-1]))
            else:
                res.extend([node_action])
        return res
    else:
        return [query]


def tree_calculations(input_data):
    tree, query_tree, create_output_string_funct, filters = input_data
    _, subtrees = tree.get_subtrees(query_tree, [], create_output_string_funct, filters)
    return subtrees


def get_unigrams(input_data):
    tree, query_tree, create_output_string_funct, filters = input_data
    unigrams = tree.get_unigrams(create_output_string_funct, filters)
    return unigrams


def tree_calculations_chunks(input_data):
    trees, query_tree, create_output_string_funct, filters = input_data

    result_dict = {}
    for tree in trees:
        _, subtrees = tree.get_subtrees(query_tree, [], create_output_string_funct, filters)

        for query_results in subtrees:
            for r in query_results:
                if r in result_dict:
                    result_dict[r] += 1
                else:
                    result_dict[r] = 1
    return result_dict


def add_node(tree):
    if 'children' in tree:
        tree['children'].append({})
    else:
        tree['children'] = [{}]


# walk over all nodes in tree and add a node to each possible node
def tree_grow(orig_tree):
    new_trees = []
    new_tree = copy.deepcopy(orig_tree)
    add_node(new_tree)
    new_trees.append(new_tree)
    if 'children' in orig_tree:
        children = []
        for child_tree in orig_tree['children']:
            children.append(tree_grow(child_tree))
        for i, child in enumerate(children):
            for child_res in child:
                new_tree = copy.deepcopy(orig_tree)
                new_tree['children'][i] = child_res
                new_trees.append(new_tree)

    return new_trees


def compare_trees(tree1, tree2):
    if tree1 == {} and tree2 == {}:
        return True

    if 'children' not in tree1 or 'children' not in tree2 or len(tree1['children']) != len(tree2['children']):
        return False

    children2_connections = []

    for child1_i, child1 in enumerate(tree1['children']):
        child_duplicated = False
        for child2_i, child2 in enumerate(tree2['children']):
            if child2_i in children2_connections:
                pass
            if compare_trees(child1, child2):
                children2_connections.append(child2_i)
                child_duplicated = True
                break
        if not child_duplicated:
            return False

    return True


def create_ngrams_query_trees(n, trees):
    for i in range(n - 1):
        new_trees = []
        for tree in trees:
            # append new_tree only if it is not already inside
            for new_tree in tree_grow(tree):
                duplicate = False
                for confirmed_new_tree in new_trees:
                    if compare_trees(new_tree, confirmed_new_tree):
                        duplicate = True
                        break
                if not duplicate:
                    new_trees.append(new_tree)

        trees = new_trees
    return trees


def count_trees(cpu_cores, all_trees, query_tree, create_output_string_functs, filters, unigrams_dict, result_dict):
    with Pool(cpu_cores) as p:
        if cpu_cores > 1:
            all_unigrams = p.map(get_unigrams, [(tree, query_tree, create_output_string_functs, filters) for tree in all_trees])
            for unigrams in all_unigrams:
                for unigram in unigrams:
                    if unigram in unigrams_dict:
                        unigrams_dict[unigram] += 1
                    else:
                        unigrams_dict[unigram] = 1

            all_subtrees = p.map(tree_calculations, [(tree, query_tree, create_output_string_functs, filters) for tree in all_trees])

            for tree_i, subtrees in enumerate(all_subtrees):

                for query_results in subtrees:
                    for r in query_results:
                        if filters['node_order']:
                            key = r.get_key() + r.order
                        else:
                            key = r.get_key()
                        if key in result_dict:
                            result_dict[key]['number'] += 1
                        else:
                            result_dict[key] = {'object': r, 'number': 1}

        # 3.65 s (1 core)
        else:
            for tree_i, tree in enumerate(all_trees):
                input_data = (tree, query_tree, create_output_string_functs, filters)
                if filters['association_measures']:
                    unigrams = get_unigrams(input_data)
                    for unigram in unigrams:
                        if unigram in unigrams_dict:
                            unigrams_dict[unigram] += 1
                        else:
                            unigrams_dict[unigram] = 1

                subtrees = tree_calculations(input_data)
                for query_results in subtrees:
                    for r in query_results:
                        if filters['node_order']:
                            key = r.get_key() + r.order
                        else:
                            key = r.get_key()
                        if key in result_dict:
                            result_dict[key]['number'] += 1
                        else:
                            result_dict[key] = {'object': r, 'number': 1}


def read_filters(configs, feats_detailed_list):
    tree_size = configs['tree_size']
    tree_size_range = tree_size.split('-')
    tree_size_range = [int(r) for r in tree_size_range]

    if tree_size_range[0] > 0:
        if len(tree_size_range) == 1:
            query_tree = create_ngrams_query_trees(tree_size_range[0], [{}])
        elif len(tree_size_range) == 2:
            query_tree = []
            for i in range(tree_size_range[0], tree_size_range[1] + 1):
                query_tree.extend(create_ngrams_query_trees(i, [{}]))
    else:
        if tree_size_range[0] == 0 and 'query' not in configs:
            raise ValueError('You should specify either tree_size or query!')
        query = configs['query']
        query_tree = [decode_query('(' + query + ')', '', feats_detailed_list)]

    # set filters
    node_type = configs['node_type']
    node_types = node_type.split('+')
    create_output_string_functs = []
    for node_type in node_types:
        assert node_type in ['deprel', 'lemma', 'upos', 'xpos', 'form', 'feats'], '"node_type" is not set up correctly'
        cpu_cores = configs['cpu_cores']
        if node_type == 'deprel':
            create_output_string_funct = create_output_string_deprel
        elif node_type == 'lemma':
            create_output_string_funct = create_output_string_lemma
        elif node_type == 'upos':
            create_output_string_funct = create_output_string_upos
        elif node_type == 'xpos':
            create_output_string_funct = create_output_string_xpos
        elif node_type == 'feats':
            create_output_string_funct = create_output_string_feats
        else:
            create_output_string_funct = create_output_string_form
        create_output_string_functs.append(create_output_string_funct)

    filters = {}
    filters['internal_saves'] = configs['internal_saves']
    filters['input'] = configs['input_path']
    filters['node_order'] = configs['node_order']
    # filters['caching'] = config.getboolean('settings', 'caching')
    filters['dependency_type'] = configs['dependency_type']
    filters['label_whitelist'] = configs['label_whitelist']
    if configs['root_whitelist']:
        # test
        filters['root_whitelist'] = []

        for option in configs['root_whitelist']:
            attribute_dict = {}
            for attribute in option.split('&'):
                value = attribute.split('=')
                attribute_dict[value[0]] = value[1]
            filters['root_whitelist'].append(attribute_dict)
    else:
        filters['root_whitelist'] = []
    filters['complete_tree_type'] = configs['complete_tree_type']
    filters['association_measures'] = configs['association_measures']
    filters['nodes_number'] = configs['nodes_number']
    filters['frequency_threshold'] = configs['frequency_threshold']
    filters['lines_threshold'] = configs['lines_threshold']
    filters['print_root'] = configs['print_root']

    return filters, query_tree, create_output_string_functs, cpu_cores, tree_size_range, node_types


def process_trees(input_path, internal_saves, configs):
    if os.path.isdir(input_path):

        checkpoint_path = Path(internal_saves, 'checkpoint.pkl') if internal_saves is not None else None
        continuation_processing = configs['continuation_processing']

        if checkpoint_path is None or not checkpoint_path.exists() or not continuation_processing:
            already_processed = set()
            result_dict = {}
            unigrams_dict = {}
            corpus_size = 0
            feats_detailed_list = {}
            if checkpoint_path is not None and checkpoint_path.exists():
                os.remove(checkpoint_path)
        else:
            already_processed, result_dict, unigrams_dict, corpus_size, feats_detailed_list = load_zipped_pickle(
                checkpoint_path)

        for path in sorted(os.listdir(input_path)):
            path_obj = Path(input_path, path)
            pathlist = path_obj.glob('**/*.conllu')
            if path_obj.name in already_processed:
                continue
            start_exe_time = time.time()
            for path in sorted(pathlist):
                # because path is object not string
                path_str = str(path)

                (all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, sub_corpus_size,
                 feats_detailed_list) = create_trees(path_str, internal_saves, feats_detailed_dict=feats_detailed_list,
                                                     save=False)

                corpus_size += sub_corpus_size

                filters, query_tree, create_output_string_functs, cpu_cores, tree_size_range, node_types = read_filters(
                    configs, feats_detailed_list)

                count_trees(cpu_cores, all_trees, query_tree, create_output_string_functs, filters, unigrams_dict,
                            result_dict)

            already_processed.add(path_obj.name)

            # 15.26
            print("Execution time:")
            print("--- %s seconds ---" % (time.time() - start_exe_time))
            save_zipped_pickle(
                (already_processed, result_dict, unigrams_dict, corpus_size, feats_detailed_list),
                checkpoint_path, protocol=2)

    else:
        # 261 - 9 grams
        # 647 - 10 grams
        # 1622 - 11 grams
        # 4126 - 12 grams
        # 10598 - 13 grams
        (all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, corpus_size,
         feats_detailed_list) = create_trees(input_path, internal_saves)

        result_dict = {}
        unigrams_dict = {}

        filters, query_tree, create_output_string_functs, cpu_cores, tree_size_range, node_types = read_filters(configs,
                                                                                                                feats_detailed_list)

        start_exe_time = time.time()
        count_trees(cpu_cores, all_trees, query_tree, create_output_string_functs, filters, unigrams_dict, result_dict)

        print("Execution time:")
        print("--- %s seconds ---" % (time.time() - start_exe_time))

    return result_dict, tree_size_range, filters, corpus_size, unigrams_dict, node_types


def get_keyness(abs_freq_A, abs_freq_B, count_A, count_B):
    E1 = count_A * (abs_freq_A + abs_freq_B) / (count_A + count_B)
    E2 = count_B * (abs_freq_A + abs_freq_B) / (count_A + count_B)

    LL = 2 * ((abs_freq_A * math.log(abs_freq_A / E1)) + (abs_freq_B * math.log(abs_freq_B / E2))) if abs_freq_B > 0 else 0
    BIC = LL - math.log(count_A + count_B) if abs_freq_B > 0 else 0
    log_ratio = math.log(((abs_freq_A/count_A)/(abs_freq_B/count_B)), 2) if abs_freq_B > 0 else 0
    OR = (abs_freq_A/(count_A-abs_freq_A)) / (abs_freq_B/(count_B-abs_freq_B)) if abs_freq_B > 0 else 0
    diff = (((abs_freq_A/count_A)*1000000 - (abs_freq_B/count_B)*1000000)*100) / ((abs_freq_B/count_B)*1000000) if abs_freq_B > 0 else 0

    if abs_freq_B <= 0:
        return [abs_freq_B, '%.1f' % (abs_freq_B * 1000000.0 / count_B), LL, BIC, log_ratio, OR, diff]
    return [abs_freq_B, '%.1f' % (abs_freq_B * 1000000.0/count_B), '%.2f' % LL, '%.2f' % BIC, '%.2f' % log_ratio, '%.2f' % OR, '%.2f' % diff]


def get_grew(nodes, links, node_types, node_order, location_mapper, dependency_type, complete):
    assert nodes
    node_result = {}
    for node in nodes:
        node_result[location_mapper[node.location]] = []
        for node_type in node_types:
            if node_type == 'deprel':
                node_result[location_mapper[node.location]].append(f'deprel={node.deprel}')
            elif node_type == 'lemma':
                node_result[location_mapper[node.location]].append(f'lemma="{node.lemma}"')
            elif node_type == 'upos':
                node_result[location_mapper[node.location]].append(f'upos={node.upos}')
            elif node_type == 'xpos':
                node_result[location_mapper[node.location]].append(f'xpos={node.xpos}')
            elif node_type == 'feats':
                for k, v in node.feats.items():
                    node_result[location_mapper[node.location]].append(f'{k}={v}')
            else:
                node_result[location_mapper[node.location]].append(f'form="{node.form}"')
    link_result = []
    order_result = []
    for link in links:
        link_result.append([location_mapper[link[0].location], location_mapper[link[1].location]])
        if node_order:
            if link[0].location < link[1].location:
                order_result.append([location_mapper[link[0].location], location_mapper[link[1].location], '<<'])
            else:
                order_result.append([location_mapper[link[0].location], location_mapper[link[1].location], '>>'])
    grew = 'pattern {'
    grew += '; '.join([node_k + ' [' + ', '.join(v) + ']' for node_k, v in node_result.items()]) + '; '
    grew += '; '.join([f'{link[0]} -[{link_node[1].deprel}]-> {link[1]}' for link, link_node in zip(link_result, links)]) if dependency_type else \
        '; '.join([f'{link[0]} -> {link[1]}' for link in link_result])
    grew += '; ' + '; '.join([f'{link[0]} {link[2]} {link[1]}' for link in order_result])

    # TODO
    # if smthing:
    #    return 'without {A -> X}'
    if complete:
        without_statements = []
        for i, key in enumerate(node_result.keys()):
            # without_statements.append('without {' + f'{key} -> X{i}' + '}')
            without_statements.append(f'without {{{key} -> X{i}}}')

        return grew + '} ' + ' '.join(without_statements)
    return grew + '}'


def create_default_configs():
    configs = {}
    # mandatory parameters
    configs['input_path'] = 'data/sl_ssj-ud_v2.4.conllu'
    configs['output'] = 'results/out_official.tsv'
    configs['tree_size'] = '2-4'
    configs['node_type'] = 'upos'

    # mandatory parameters with default value
    configs['internal_saves'] = './internal_saves'
    configs['cpu_cores'] = 12
    configs['complete_tree_type'] = True
    configs['dependency_type'] = True
    configs['node_order'] = True
    configs['association_measures'] = False

    configs['label_whitelist'] = []
    configs['root_whitelist'] = []

    configs['query'] = None

    configs['compare'] = None

    configs['frequency_threshold'] = 0
    configs['lines_threshold'] = None

    configs['continuation_processing'] = False

    configs['nodes_number'] = True
    configs['print_root'] = True

    if configs['compare'] is not None:
        configs['other_input_path'] = configs['compare']
    return configs


def read_configs(config, args):
    configs = {}
    # mandatory parameters
    configs['input_path'] = config.get('settings', 'input') if not args.input else args.input
    configs['output'] = config.get('settings', 'output') if not args.output else args.output
    configs['tree_size'] = config.get('settings', 'size', fallback='0') if not args.size else args.size
    configs['node_type'] = config.get('settings', 'node_type') if not args.node_type else args.node_type

    # mandatory parameters with default value
    configs['internal_saves'] = (config.get('settings', 'internal_saves') if not args.internal_saves else args.internal_saves) if config.has_option('settings', 'internal_saves') else None
    configs['cpu_cores'] = (config.getint('settings', 'cpu_cores') if not args.cpu_cores else args.cpu_cores) if config.has_option('settings', 'cpu_cores') else max(cpu_count() - 1, 1)
    configs['complete_tree_type'] = (config.getboolean('settings', 'complete') if not args.complete else args.complete == 'yes')
    configs['dependency_type'] = (config.getboolean('settings', 'labeled') if not args.labeled else args.labeled == 'yes')
    configs['node_order'] = (config.getboolean('settings', 'fixed') if not args.fixed else args.fixed == 'yes')
    configs['association_measures'] = (config.getboolean('settings',
                                                        'association_measures') if not args.association_measures else args.association_measures == 'yes')

    # optional parameters
    if config.has_option('settings', 'labels'):
        label_whitelist = config.get('settings',
                                     'labels') if not args.labels else args.labels
        configs['label_whitelist'] = label_whitelist.split('|')
    else:
        configs['label_whitelist'] = []

    if config.has_option('settings', 'root'):
        root_whitelist = config.get('settings',
                                    'root') if not args.root else args.root
        configs['root_whitelist'] = root_whitelist.split('|')
    else:
        configs['root_whitelist'] = []

    if config.has_option('settings', 'query') or args.query:
        # configs['tree_size'] = '0'
        configs['query'] = (config.get('settings', 'query') if not args.query else args.query)

    if args.compare:
        configs['compare'] = args.compare
    else:
        configs['compare'] = config.get('settings', 'compare') if config.has_option('settings', 'compare') else None

    configs['frequency_threshold'] = config.getfloat('settings', 'frequency_threshold') if not args.frequency_threshold else args.frequency_threshold
    configs['lines_threshold'] = config.getint('settings', 'max_lines') if not args.max_lines else args.max_lines

    configs['continuation_processing'] = config.getboolean('settings', 'continuation_processing',
                                                fallback=False) if not args.continuation_processing else args.input

    configs['grew_match'] = config.getboolean('settings',
                                              'grew_match') if not args.grew_match else args.grew_match == 'yes'
    configs['depsearch'] = config.getboolean('settings',
                                             'depsearch') if not args.depsearch else args.depsearch == 'yes'

    configs['nodes_number'] = True
    configs['print_root'] = True

    if configs['compare'] is not None:
        configs['other_input_path'] = configs['compare']
    return configs


def write(configs, result_dict, tree_size_range, filters, corpus_size, unigrams_dict, node_types,
          other_result_dict=None, other_corpus_size=None):
    sorted_list = sorted(result_dict.items(), key=lambda x: x[1]['number'], reverse=True)

    with open(os.path.join(here, 'codes_mapper.json'), 'r') as f:
        codes_mapper = json.load(f)
    path = Path(configs['input_path']).name
    lang = path.split('_')[0]
    corpus_name = path.split('_')[1].split('-')[0].lower() if len(path.split('_')) > 1 else 'unknown'
    corpus = codes_mapper[lang][corpus_name] if lang in codes_mapper and corpus_name in codes_mapper[lang] else None

    with open(configs['output'], "w", newline="", encoding="utf-8") as f:
        # header - use every second space as a split
        writer = csv.writer(f, delimiter='\t')
        if tree_size_range[-1]:
            len_words = tree_size_range[-1]
        else:
            len_words = int(len(configs['query'].split(" ")) / 2 + 1)
        header = ["Tree"] + ["Node " + string.ascii_uppercase[i] + "-" + node_type for i in range(len_words) for
                             node_type in node_types] + ['Absolute frequency']
        header += ['Relative frequency']
        if filters['node_order']:
            header += ['Order']
        if configs['grew_match']:
            header += ['Grew-match query']
        if corpus and configs['grew_match']:
            header += ['Grew-match URL']
        if filters['node_order'] and configs['depsearch']:
            header += ['Depsearch tree query']
        if filters['nodes_number']:
            header += ['Number of nodes']
        if filters['print_root']:
            header += ['Root node']
        if filters['association_measures']:
            header += ['MI', 'MI3', 'Dice', 'logDice', 't-score', 'simple-LL']
        if configs['compare']:
            header += ['Absolute frequency in compared treebank', 'Relative frequency in compared treebank', 'LL',
                       'BIC', 'Log ratio', 'OR', '%DIFF']
        writer.writerow(header)

        if filters['lines_threshold']:
            sorted_list = sorted_list[:filters['lines_threshold']]

        # body
        for k, v in sorted_list:
            v['object'].get_array()
            relative_frequency = v['number'] * 1000000.0 / corpus_size
            if filters['frequency_threshold'] and filters['frequency_threshold'] > v['number']:
                break
            words_only = [word_att for word in v['object'].array for word_att in word] + ['' for i in range(
                (tree_size_range[-1] - len(v['object'].array)) * len(v['object'].array[0]))]
            key = v['object'].get_key()[1:-1] if v['object'].get_key()[0] == '(' and v['object'].get_key()[
                -1] == ')' else v['object'].get_key()
            grew_nodes, grew_links = v['object'].get_grew()
            location_mapper = v['object'].get_location_mapper()
            key_grew = get_grew(grew_nodes, grew_links, node_types, filters['node_order'], location_mapper,
                                filters['dependency_type'], filters['complete_tree_type'])
            filters['complete_tree_type'] = False
            row = [key] + words_only + [str(v['number'])]
            row += ['%.1f' % relative_frequency]
            if filters['node_order']:
                row += [v['object'].order]
            if configs['grew_match']:
                row += [key_grew]
            if corpus and configs['grew_match']:
                url = f'http://universal.grew.fr/?corpus={corpus}&request={urllib.parse.quote(key_grew)}'
                row += [url]
            if filters['node_order'] and configs['depsearch']:
                row += [v['object'].get_key_sorted()[1:-1]]
            if filters['nodes_number']:
                row += ['%d' % len(v['object'].array)]
            if filters['print_root']:
                row += [v['object'].node.name]
            if filters['association_measures']:
                row += get_collocabilities(v, unigrams_dict, corpus_size)
            if configs['compare']:
                other_abs_freq = other_result_dict[k]['number'] if k in other_result_dict else 0
                row += get_keyness(v['number'], other_abs_freq, corpus_size, other_corpus_size)
            writer.writerow(row)


def run(configs):
    result_dict, tree_size_range, filters, corpus_size, unigrams_dict, node_types = process_trees(configs['input_path'],
                                                                                                  configs[
                                                                                                      'internal_saves'],
                                                                                                  configs)

    other_result_dict, other_corpus_size = None, None
    if configs['compare'] is not None:
        other_result_dict, other_tree_size_range, other_filters, other_corpus_size, other_unigrams_dict, other_node_types = process_trees(
            configs['other_input_path'], configs['internal_saves'], configs)

    write(configs, result_dict, tree_size_range, filters, corpus_size, unigrams_dict, node_types, other_result_dict,
          other_corpus_size)
