# Copyright 2024 CJVT
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

import copy
from stark.resources.constants import UNIVERSAL_FEATURES


def add_node(tree):
    """
    Adds node to a tree.
    :param tree:
    :return:
    """
    if 'children' in tree:
        tree['children'].append({})
    else:
        tree['children'] = [{}]


def tree_grow(orig_tree):
    """
    Walks over all nodes in tree and add a node to each possible node.
    :param orig_tree:
    :return:
    """
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
    """
    Compares two trees and returns True, when they match.
    :param tree1:
    :param tree2:
    :return:
    """
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
    """
    Forms unique ngram query trees.
    :param n:
    :param trees:
    :return:
    """
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


def split_query_text(input_string):
    """
    Splits query by ignoring everything in brackets and otherwise splitting by spaces.
    :param input_string: Raw query in string
    :return: Split string
    """

    replacements = {}
    brackets_count = 1
    brackets_depth = 0
    replace_string = ''

    for char in input_string:
        if char == '(':
            brackets_depth += 1

        if brackets_depth >= 1:
            replace_string += char

        if char == ')':
            brackets_depth -= 1
            if brackets_depth == 0:
                input_string = input_string.replace(replace_string, f'<BRACKET{brackets_count}>', 1)
                replacements[f'<BRACKET{brackets_count}>'] = replace_string
                brackets_count += 1
                replace_string = ''

    return [el if el not in replacements else replacements[el] for el in input_string.split()]


def decode_query(orig_query, dependency_type):
    """
    Reads query and returns it in tree-form dictionary.
    :param orig_query:
    :param dependency_type:
    :return:
    """
    new_query = False

    # if command in bracelets remove them and treat command as new query
    if orig_query[0] == '(' and orig_query[-1] == ')':
        new_query = True
        orig_query = orig_query[1:-1]

    decoded_query = {'restrictions': []}
    if dependency_type != '':
        dependency_restrictions = []
        for dependency_type_el in dependency_type.split('|'):
            dependency_type_el = dependency_type_el[1:]
            if dependency_type_el and dependency_type_el[0] == '!':
                negation = True
                dependency_type_el = dependency_type_el[1:]
            else:
                negation = False
            if dependency_type_el:
                dependency_restrictions.append((negation, dependency_type_el))
    else:
        dependency_restrictions = None

    if orig_query == '_':
        if dependency_restrictions:
            decoded_query['restrictions'] = [{'deprel': dependency_restriction}
                                             for dependency_restriction in dependency_restrictions]
        return decoded_query
    # if no spaces in query then this is query node and do this otherwise further split query
    elif len(orig_query.split(' ')) == 1:
        for orig_query_or_split_parts in orig_query.split(' ')[0].split('|'):
            restriction = {}
            orig_query_split_parts = orig_query_or_split_parts.split(' ')[0].split('&')
            for orig_query_split_part in orig_query_split_parts:
                if orig_query_split_part[0] == '!' and len(orig_query_split_part) > 1:
                    negation = True
                    orig_query_split_part = orig_query_split_part[1:]
                else:
                    negation = False
                orig_query_split = orig_query_split_part.split('=', 1)
                if len(orig_query_split) > 1:
                    if orig_query_split[0] == 'L':
                        restriction['lemma'] = (negation, orig_query_split[1])
                    elif orig_query_split[0] == 'upos':
                        restriction['upos'] = (negation, orig_query_split[1])
                    elif orig_query_split[0] == 'xpos':
                        restriction['xpos'] = (negation, orig_query_split[1])
                    elif orig_query_split[0] == 'form':
                        restriction['form'] = (negation, orig_query_split[1])
                    elif orig_query_split[0] == 'feats':
                        restriction['feats'] = (negation, orig_query_split[1])
                    elif orig_query_split[0] in UNIVERSAL_FEATURES:
                        restriction['feats_detailed'] = {}
                        restriction['feats_detailed'][orig_query_split[0]] = (negation, orig_query_split[1])
                    elif not new_query:
                        raise Exception('Not supported yet!')
                    else:
                        raise Exception('Unexpected behaviour!')
                elif not new_query:
                    restriction['form'] = (negation, orig_query_split_part)
            decoded_query['restrictions'].append(restriction)

        # merge restrictions from dependencies and other restrictions (this solves 'or' cases in both simultaneously)
        if dependency_restrictions:
            new_restrictions = []
            for dependency_restriction in dependency_restrictions:
                for restriction in decoded_query['restrictions']:
                    new_restriction = restriction.copy()
                    new_restriction['deprel'] = dependency_restriction
                    new_restrictions.append(new_restriction)
            decoded_query['restrictions'] = new_restrictions
        return decoded_query

    # split over spaces if not inside braces
    all_orders = split_query_text(orig_query)

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
            children.append(decode_query(node_action, priority_actions[i]))
        elif i > root_index:
            children.append(decode_query(node_action, priority_actions[i - 1]))
        else:
            root = decode_query(node_action, dependency_type)
    if children:
        root["children"] = children
    return root


def generate_query_trees(configs, filters):
    """
    Generates query trees based on configs and filters.
    :param configs:
    :param filters:
    :return:
    """
    query_tree = []
    if filters['tree_size_range'][0] > 0:
        if len(filters['tree_size_range']) == 1:
            query_tree = create_ngrams_query_trees(filters['tree_size_range'][0], [{}])
        elif len(filters['tree_size_range']) == 2:
            query_tree = []
            for i in range(filters['tree_size_range'][0], filters['tree_size_range'][1] + 1):
                query_tree.extend(create_ngrams_query_trees(i, [{}]))
    else:
        if filters['tree_size_range'][0] == 0 and 'query' not in configs:
            raise ValueError('You should specify either tree_size or query!')
        query = configs['query']
        query_tree = [decode_query('(' + query + ')', '')]
        if query_tree == [{}]:
            raise ValueError('Query is not formatted properly!')

    return query_tree


def get_query_tree_size(query_tree):
    """
    Returns size of specific query tree.
    :param query_tree:
    :return:
    """
    size = 1
    if 'children' in query_tree:
        for child in query_tree['children']:
            size += get_query_tree_size(child)

    return size


def get_query_tree_size_range(query_trees):
    """
    Returns tree size range.
    :param query_trees:
    :return:
    """
    min_size = 1000000
    max_size = 0
    for query_tree in query_trees:
        size = get_query_tree_size(query_tree)
        if size > max_size:
            max_size = size
        if size < min_size:
            min_size = size
    return [min_size, max_size]
