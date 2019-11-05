import argparse
import configparser
import csv
import hashlib
import os
import pickle
import re

import pyconll

from Tree import Tree, create_output_string_form, create_output_string_deprel, create_output_string_lemma, create_output_string_upos, create_output_string_xpos

# for separate searches of feats
# feats_list = [
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
#
# feats_dict = {key: {} for key in feats_list}


def decode_query(orig_query, dependency_type):
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
                # elif orig_query_split[0] in feats_list:
                #     decoded_query['feats'] = {}
                #     decoded_query['feats'][orig_query_split[0]] = orig_query_split[1]
                #     return decoded_query
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
            children.append(decode_query(node_action, priority_actions[i][1:]))
        elif i > root_index:
            children.append(decode_query(node_action, priority_actions[i - 1][1:]))
        else:
            root = decode_query(node_action, dependency_type)
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

        form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, feats_complete_dict = {}, {}, {}, {}, {}, {}

        all_trees = []

        for sentence in train:
            root = None
            root_id = None
            token_nodes = []
            for token in sentence:
                # token_feats = ''
                # for k, v in token.feats.items():
                #     token_feats += k + next(iter(v)) + '|'
                # token_feats = token_feats[:-1]
                # TODO check if 5th place is always there for feats
                token_feats = token._fields[5]
                node = Tree(token.form, token.lemma, token.upos, token.xpos, token.deprel, token_feats, form_dict,
                            lemma_dict, upos_dict, xpos_dict, deprel_dict, None, feats_complete_dict, token.head)
                token_nodes.append(node)
                if token.deprel == 'root':
                    root = node
                    root_id = int(token.id)

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
            pickle.dump((all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict), output)
    else:
        print('Reading trees:')
        print('Completed')
        with open(trees_read_outputfile, 'rb') as pkl_file:
            (all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict) = pickle.load(pkl_file)

    return all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict


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
            res.extend(printable_answers(node_action))
        return res
    else:
        return [query]

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
    ngrams = 0
    if config.getint('settings', 'ngrams') == 2:
        ngrams = 2
        query_tree = [{"children": [{}]}]
    elif config.getint('settings', 'ngrams') == 3:
        ngrams = 3
        query_tree = [{"children": [{}, {}]}, {"children": [{"children": [{}]}]}]
    elif config.getint('settings', 'ngrams') == 4:
        ngrams = 4
        query_tree = [{"children": [{}, {}, {}]}, {"children": [{"children": [{}, {}]}]}, {"children": [{"children": [{}]}, {}]}, {"children": [{"children": [{"children": [{}]}]}]}]
    elif config.getint('settings', 'ngrams') == 5:
        ngrams = 5
        query_tree = [{"children": [{}, {}, {}, {}]}, {"children": [{"children": [{}]}, {}, {}]}, {"children": [{"children": [{}, {}]}, {}]}, {"children": [{"children": [{}]}, {"children": [{}]}]},
                      {"children": [{"children": [{"children": [{}]}]}, {}]}, {"children": [{"children": [{"children": [{}]}, {}]}]}, {"children": [{"children": [{"children": [{}, {}]}]}]},
                      {"children": [{"children": [{"children": [{"children": [{}]}]}]}]}]
    else:
        query_tree = [decode_query('(' + config.get('settings', 'query') + ')', '')]
        # order_independent_queries(query_tree)

    (all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict) = create_trees(config)


    # set filters
    assert config.get('settings', 'node_type') in ['deprel', 'lemma', 'upos', 'xpos', 'form'], '"node_type" is not set up correctly'
    if config.get('settings', 'node_type') == 'deprel':
        create_output_string_funct = create_output_string_deprel
    elif config.get('settings', 'node_type') == 'lemma':
        create_output_string_funct = create_output_string_lemma
    elif config.get('settings', 'node_type') == 'upos':
        create_output_string_funct = create_output_string_upos
    elif config.get('settings', 'node_type') == 'xpos':
        create_output_string_funct = create_output_string_xpos
    else:
        create_output_string_funct = create_output_string_form

    result_dict = {}
    filters = {}
    filters['node_order'] = config.getboolean('settings', 'node_order')

    # for tree in all_trees[2:]:
    # for tree in all_trees[1205:]:
    for tree in all_trees:
        # original
        # r_children = tree.r_children[:1] + tree.r_children[3:4]
        # tree.r_children = tree.r_children[:1] + tree.r_children[2:4]
        _, _, subtrees = tree.get_subtrees(query_tree, [], create_output_string_funct, filters)
        for query_results in subtrees:
            for result in query_results:
                # if ngrams:
                #     result = sorted(result)
                # r = tuple(result)
                r = result
                if r in result_dict:
                    result_dict[r] += 1
                else:
                    result_dict[r] = 1
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

    sorted_list = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)

    with open(config.get('settings', 'output'), "w", newline="") as f:
        # header - use every second space as a split
        writer = csv.writer(f, delimiter='\t')
        if ngrams:
            len_words = ngrams
        else:
            len_words = int(len(config.get('settings', 'query').split(" "))/2 + 1)
        header = ["Structure"] + ["Word #" + str(i) for i in range(1, len_words + 1)] + ['Number of occurences']
        # header = [" ".join(words[i:i + span]) for i in range(0, len(words), span)] + ['Number of occurences']
        writer.writerow(header)

        # body
        for k, v in sorted_list:
            words_only = printable_answers(k)
            writer.writerow([k] + words_only + [str(v)])

    return


if __name__ == "__main__":
    main()
