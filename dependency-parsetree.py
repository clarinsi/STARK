import argparse
import configparser
import copy
import csv
import hashlib
import os
import pickle
import re
import string
import time
import timeit
from multiprocessing import Pool

import pyconll

from Tree import Tree, create_output_string_form, create_output_string_deprel, create_output_string_lemma, create_output_string_upos, create_output_string_xpos, create_output_string_feats

# for separate searches of feats
# feats_detailed_list = [
#     # lexical features
#     'PronType', 'NumType', 'Poss', 'Reflex', 'Foreign', 'Abbr',
#
#     # Inflectional features (nominal)
#     'Gender', 'Animacy', 'NounClass', 'Number', 'Case', 'Definite', 'Degree',
#
#     # Inflectional features (verbal)
#     'VerbForm', 'Mood', 'Tense', 'Aspect', 'Voice', 'Evident', 'Polarity', 'Person', 'Polite', 'Clusivity',
#
#     # Other
#     'Variant', 'Number[psor]', 'Gender[psor]', 'NumForm'
# ]

# feats_detailed_list = []

# feats_detailed_dict = {key: {} for key in feats_detailed_list}
from generic import get_collocabilities


def decode_query(orig_query, dependency_type, feats_detailed_list):
    new_query = False

    # if command in bracelets remove them and treat command as new query
    if orig_query[0] == '(' and orig_query[-1] == ')':
        new_query = True
        orig_query = orig_query[1:-1]

    # if orig_query is '_' return {}
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
                    # return decoded_query
                elif orig_query_split[0] == 'upos':
                    decoded_query['upos'] = orig_query_split[1]
                    # return decoded_query
                elif orig_query_split[0] == 'xpos':
                    decoded_query['xpos'] = orig_query_split[1]
                    # return decoded_query
                elif orig_query_split[0] == 'form':
                    decoded_query['form'] = orig_query_split[1]
                    # return decoded_query
                elif orig_query_split[0] == 'feats':
                    decoded_query['feats'] = orig_query_split[1]
                    # return decoded_query
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
                # return decoded_query
        return decoded_query

    # split over spaces if not inside braces
    # PATTERN = re.compile(r'''((?:[^ ()]|\([^.]*\))+)''')
    # all_orders = PATTERN.split(orig_query)
    # PATTERN = re.compile(r"(?:[^ ()]|\([^.]*\))+")
    # all_orders = re.findall(r"(?:[^ ()]|\([^]*\))+", orig_query)
    all_orders = re.split(r"\s+(?=[^()]*(?:\(|$))", orig_query)


    # all_orders = orig_query.split()
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


def create_trees(config):
    internal_saves = config.get('settings', 'internal_saves')
    input_path = config.get('settings', 'input')
    hash_object = hashlib.sha1(input_path.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    trees_read_outputfile = os.path.join(internal_saves, hex_dig)

    if not os.path.exists(trees_read_outputfile):

        train = pyconll.load_from_file(input_path)

        form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, feats_dict = {}, {}, {}, {}, {}, {}

        all_trees = []
        corpus_size = 0
        feats_detailed_dict = {}

        for sentence in train:
            root = None
            root_id = None
            token_nodes = []
            for token in sentence:
                # token_feats = ''
                # for k, v in token.feats.items():
                #     token_feats += k + next(iter(v)) + '|'
                # token_feats = token_feats[:-1]
                if not token.id.isdigit():
                    continue

                # TODO check if 5th place is always there for feats
                feats = token._fields[5]
                node = Tree(int(token.id), token.form, token.lemma, token.upos, token.xpos, token.deprel, feats, token.feats, form_dict,
                            lemma_dict, upos_dict, xpos_dict, deprel_dict, feats_dict, feats_detailed_dict, token.head)
                token_nodes.append(node)
                if token.deprel == 'root':
                    root = node

                corpus_size += 1

            for token_id, token in enumerate(token_nodes):
                if int(token.parent) == 0:
                    token.set_parent(None)
                else:
                    parent_id = int(token.parent) - 1
                    # if token_id < parent_id:
                    #     token_nodes[parent_id].add_l_child(token)
                    # elif token_id > parent_id:
                    #     token_nodes[parent_id].add_r_child(token)
                    # else:
                    #     raise Exception('Root element should not be here!')
                    if token_nodes[parent_id].children_split == -1 and token_id > parent_id:
                        token_nodes[parent_id].children_split = len(token_nodes[parent_id].children)
                    token_nodes[parent_id].add_child(token)
                    token.set_parent(token_nodes[parent_id])

            for token in token_nodes:
                if token.children_split == -1:
                    token.children_split = len(token.children)

            if root == None:
                raise Exception('No root element in sentence!')
            all_trees.append(root)


        with open(trees_read_outputfile, 'wb') as output:
            pickle.dump((all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, corpus_size, feats_detailed_dict), output)
    else:
        print('Reading trees:')
        print('Completed')
        with open(trees_read_outputfile, 'rb') as pkl_file:
            (all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, corpus_size, feats_detailed_dict) = pickle.load(pkl_file)

    return all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, corpus_size, feats_detailed_dict


# def order_independent_queries(query_tree):
#     all_children = query_tree['l_children'] + query_tree['r_children']
#     if all_children > 0:
#
#     else:
#         return query_tree
#     pass

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


def chunkify(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


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
        # delete_duplicates(trees)
        # print('here')
    # tree_grow(tree)
    # tree_grow(tree)
    # tree['children'] = [{}]
    return trees


def main():
    parser = argparse.ArgumentParser()

    ## Required parameters
    parser.add_argument("--config_file",
                        default=None,
                        type=str,
                        required=True,
                        help="The input config file.")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config_file)
    # a = args.config_file
    # config.read('config.ini')
    # create queries
    tree_size = 0

    # 261 - 9 grams
    # 647 - 10 grams
    # 1622 - 11 grams
    # 4126 - 12 grams
    # 10598 - 13 grams
    (all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, corpus_size,
     feats_detailed_list) = create_trees(config)



    # if config.getint('settings', 'tree_size') == 2:
    #     tree_size = 2
    #     query_tree = [{"children": [{}]}]
    # elif config.getint('settings', 'tree_size') == 3:
    #     tree_size = 3
    #     query_tree = [{"children": [{}, {}]}, {"children": [{"children": [{}]}]}]
    # elif config.getint('settings', 'tree_size') == 4:
    #     tree_size = 4
    #     query_tree = [{"children": [{}, {}, {}]}, {"children": [{"children": [{}, {}]}]}, {"children": [{"children": [{}]}, {}]}, {"children": [{"children": [{"children": [{}]}]}]}]
    # elif config.getint('settings', 'tree_size') == 5:
    #     tree_size = 5
    #     query_tree = [{"children": [{}, {}, {}, {}]}, {"children": [{"children": [{}]}, {}, {}]}, {"children": [{"children": [{}, {}]}, {}]}, {"children": [{"children": [{}]}, {"children": [{}]}]},
    #                   {"children": [{"children": [{"children": [{}]}]}, {}]}, {"children": [{"children": [{"children": [{}]}, {}]}]}, {"children": [{"children": [{"children": [{}, {}]}]}]},
    #                   {"children": [{"children": [{"children": [{"children": [{}]}]}]}]}, {'children': [{'children': [{}, {}, {}]}]}]
    tree_size_range = config.get('settings', 'tree_size').split('-')
    tree_size_range = [int(r) for r in tree_size_range]

    if tree_size_range[0] > 1:
        if len(tree_size_range) == 1:
            query_tree = create_ngrams_query_trees(tree_size_range[0], [{}])
        elif len(tree_size_range) == 2:
            query_tree = []
            for i in range(tree_size_range[0], tree_size_range[1] + 1):
                query_tree.extend(create_ngrams_query_trees(i, [{}]))
    else:
        query_tree = [decode_query('(' + config.get('settings', 'query') + ')', '', feats_detailed_list)]
        # order_independent_queries(query_tree)


    # set filters
    node_types = config.get('settings', 'node_type').split('+')
    create_output_string_functs = []
    for node_type in node_types:
        assert node_type in ['deprel', 'lemma', 'upos', 'xpos', 'form', 'feats'], '"node_type" is not set up correctly'
        cpu_cores = config.getint('settings', 'cpu_cores')
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

    result_dict = {}
    unigrams_dict = {}
    filters = {}
    filters['node_order'] = config.get('settings', 'node_order') == 'fixed'
    # filters['caching'] = config.getboolean('settings', 'caching')
    filters['dependency_type'] = config.get('settings', 'dependency_type') == 'labeled'
    if config.has_option('settings', 'label_whitelist'):
        filters['label_whitelist'] = config.get('settings', 'label_whitelist').split('|')
    else:
        filters['label_whitelist'] = []

    if config.has_option('settings', 'root_whitelist'):
        # test
        filters['root_whitelist'] = []

        for option in config.get('settings', 'root_whitelist'). split('|'):
            attribute_dict = {}
            for attribute in option.split('&'):
                value = attribute.split('=')
                # assert value[0] in ['deprel', 'lemma', 'upos', 'xpos', 'form',
                #                     'feats'], '"root_whitelist" is not set up correctly'
                attribute_dict[value[0]] = value[1]
            filters['root_whitelist'].append(attribute_dict)
        # filters['root_whitelist'] = [{'upos': 'NOUN', 'Case': 'Nom'}, {'upos': 'ADJ', 'Degree': 'Sup'}]
    else:
        filters['root_whitelist'] = []

    filters['complete_tree_type'] = config.get('settings', 'tree_type') == 'complete'
    filters['association_measures'] = config.getboolean('settings', 'association_measures')
    filters['nodes_number'] = config.getboolean('settings', 'nodes_number')
    filters['frequency_threshold'] = config.getfloat('settings', 'frequency_threshold')
    filters['lines_threshold'] = config.getint('settings', 'lines_threshold')
    filters['print_root'] = config.getboolean('settings', 'print_root')


    # for tree in all_trees[2:]:
    # for tree in all_trees[1205:]:
    with Pool(cpu_cores) as p:
        start_exe_time = time.time()
        # 1.25 s (16 cores)
        # chunked_trees = list(chunkify(all_trees, cpu_cores))
        # if cpu_cores > 1:
        #     part_results = p.map(tree_calculations_chunks,
        #                          [(tree, query_tree, create_output_string_funct, filters) for tree in chunked_trees])
        #
        #     for part_result in part_results:
        #         for r_k, r_v in part_result.items():
        #             if r_k in result_dict:
        #                 result_dict[r_k] += r_v
        #             else:
        #                 result_dict[r_k] = r_v
        # 1.02 s (16 cores)
        if cpu_cores > 1:
            # input_data = (tree, query_tree, create_output_string_functs, filters)
            all_unigrams = p.map(get_unigrams, [(tree, query_tree, create_output_string_functs, filters) for tree in all_trees])
            for unigrams in all_unigrams:
                for unigram in unigrams:
                    if unigram in unigrams_dict:
                        unigrams_dict[unigram] += 1
                    else:
                        unigrams_dict[unigram] = 1

            all_subtrees = p.map(tree_calculations, [(tree, query_tree, create_output_string_functs, filters) for tree in all_trees])

            # for subtrees in all_subtrees:
            for tree_i, subtrees in enumerate(all_subtrees):
                for query_results in subtrees:
                    for r in query_results:
                        if filters['node_order']:
                            key = r.key + r.order
                        else:
                            key = r.key
                        # if r == '(" < , < je < velik) < tem':
                        #     print(tree_i)
                        # if r in result_dict:
                        #     result_dict[r] += 1
                        # else:
                        #     result_dict[r] = 1
                        if key in result_dict:
                            result_dict[key]['number'] += 1
                        else:
                            result_dict[key] = {'object': r, 'number': 1}

        # 3.65 s (1 core)
        else:
            # for tree_i, tree in enumerate(all_trees[-5:]):
            # for tree_i, tree in enumerate(all_trees):
            for tree_i, tree in enumerate(all_trees[1:]):
                input_data = (tree, query_tree, create_output_string_functs, filters)
                if filters['association_measures']:
                    unigrams = get_unigrams(input_data)
                    for unigram in unigrams:
                        if unigram in unigrams_dict:
                            unigrams_dict[unigram] += 1
                        else:
                            unigrams_dict[unigram] = 1
            # for tree_i, tree in enumerate(all_trees[1:]):
            # text = Če pa ostane odrasel otrok doma, se starši le težko sprijaznijo s tem, da je "velik", otrok pa ima ves čas občutek, da se njegovi starši po nepotrebnem vtikajo v njegovo življenje.
            # for tree_i, tree in enumerate(all_trees[5170:]):
            # for tree in all_trees:
                subtrees = tree_calculations(input_data)
                for query_results in subtrees:
                    for r in query_results:
                        if filters['node_order']:
                            key = r.key + r.order
                        else:
                            key = r.key
                        # if r == '(" < , < je < velik) < tem':
                        #     print(tree_i)
                        if key in result_dict:
                            result_dict[key]['number'] += 1
                        else:
                            result_dict[key] = {'object': r, 'number': 1}

        print("Execution time:")
        print("--- %s seconds ---" % (time.time() - start_exe_time))
            # test 1 layer queries
            # # tree.r_children = []
            # # tree.children[1].children = []
            # # query = [{'children': [{}]}, {'children': [{}]}]
            # # query = [{"children": [{}, {}]}, {"children": [{}]}, {"children": [{}, {}, {}]}]
            # query = [{"children": [{'form': 'je'}, {}]}, {"children": [{'form': 'je'}]}, {"children": [{'form': 'je'}, {}, {}]}]
            # # query = [{'q1':'', "children": [{'a1':''}, {'a2':''}]}, {'q2':'', "children": [{'b1':''}]}, {'q3':'', "children": [{'c1':''}, {'c2':''}, {'c3':''}]}]
            # _, _, subtrees = tree.get_subtrees(query, [], create_output_string_funct)
            # # _, subtrees = tree.get_subtrees([{'q1':'', "children": [{'a1':''}, {'a2':''}], "children": []}, {'q2':'', "children": [{'b1':''}], "children": []}, {'q3':'', "children": [{'c1':''}, {'c2':''}, {'c3':''}], "children": []}], [])
            # print('HERE!')

            # test 2 layer queries
            # tree.r_children = [Tree('je', '', '', '', '', form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, None)]
            # tree.l_children[1].l_children = []
            # new_tree = Tree('bil', '', '', '', '', form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, None)
            # new_tree.l_children = [tree]
            # _, subtrees = new_tree.get_subtrees(
            #     [{"l_children":[{"l_children": [{'a1': ''}, {'a2': ''}, {'a3': ''}, {'a4': ''}]}]}], [])
            # # _, subtrees = new_tree.get_subtrees(
            # #     [{"l_children":[{"l_children": [{'a1': ''}, {'a2': ''}, {'a3': ''}, {'a4': ''}], "r_children": []}],  "r_children": []}], [])
    sorted_list = sorted(result_dict.items(), key=lambda x: x[1]['number'], reverse=True)

    with open(config.get('settings', 'output'), "w", newline="") as f:
        # header - use every second space as a split
        writer = csv.writer(f, delimiter='\t')
        if tree_size_range[-1]:
            len_words = tree_size_range[-1]
        else:
            len_words = int(len(config.get('settings', 'query').split(" "))/2 + 1)
        header = ["Structure"] + ["Node " + string.ascii_uppercase[i] + "-" + node_type for i in range(len_words) for node_type in node_types] + ['Absolute frequency']
        header += ['Relative frequency']
        if filters['node_order']:
            header += ['Order']
        if filters['nodes_number']:
            header += ['Number of nodes']
        if filters['print_root']:
            header += ['Root node']
        if filters['association_measures']:
            header += ['MI', 'MI3', 'Dice', 't-score', 'simple-LL']
        # header = [" ".join(words[i:i + span]) for i in range(0, len(words), span)] + ['Absolute frequency']
        writer.writerow(header)

        if filters['lines_threshold']:
            sorted_list = sorted_list[:filters['lines_threshold']]

        # body
        for k, v in sorted_list:
            absolute_frequency = v['number'] * 1000000.0 / corpus_size
            if filters['frequency_threshold'] and filters['frequency_threshold'] > absolute_frequency:
                break
            words_only = [word_att for word in v['object'].array for word_att in word] + ['' for i in range((tree_size_range[-1] - len(v['object'].array)) * len(v['object'].array[0]))]
            # words_only = printable_answers(k)
            row = [v['object'].key] + words_only + [str(v['number'])]
            row += ['%.4f' % absolute_frequency]
            if filters['node_order']:
                row += [v['object'].order]
            if filters['nodes_number']:
                row += ['%d' % len(v['object'].array)]
            if filters['print_root']:
                row += [v['object'].root]
            if filters['association_measures']:
                row += get_collocabilities(v, unigrams_dict, corpus_size)
            writer.writerow(row)

    return "Done"


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Total:")
    print("--- %s seconds ---" % (time.time() - start_time))
