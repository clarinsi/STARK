import configparser
import hashlib
import os
import pickle
import re

import pyconll

from Tree import Tree


def decode_query(orig_query):
    new_query = False

    # if command in bracelets remove them and treat command as new query
    if orig_query[0] == '(' and orig_query[-1] == ')':
        new_query = True
        orig_query = orig_query[1:-1]

    # if orig_query is '_' return {}
    if orig_query == '_':
        return {}
    elif not new_query:
        raise Exception('Not supported yet!')

    # split over spaces if not inside braces
    PATTERN = re.compile(r'''((?:[^ ()]|\([^(]*\))+)''')
    all_orders = PATTERN.split(orig_query)[1::2]


    # all_orders = orig_query.split()
    node_actions = all_orders[::2]
    priority_actions = all_orders[1::2]
    priority_actions_beginnings = [a[0] for a in priority_actions]

    # find root index
    try:
        root_index = priority_actions_beginnings.index('>')
    except ValueError:
        root_index = len(priority_actions)

    l_children = []
    r_children = []
    root = None
    for i, node_action in enumerate(node_actions):
        if i < root_index:
            l_children.append(decode_query(node_action))
        elif i > root_index:
            r_children.append(decode_query(node_action))
        else:
            root = decode_query(node_action)
    root["l_children"] = l_children
    root["r_children"] = r_children
    return root


def create_trees(config):
    internal_saves = config.get('settings', 'internal_saves')
    input_path = config.get('settings', 'input')
    hash_object = hashlib.sha1(input_path.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    trees_read_outputfile = os.path.join(internal_saves, hex_dig)

    if not os.path.exists(trees_read_outputfile):

        train = pyconll.load_from_file(input_path)

        form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict = {}, {}, {}, {}, {}

        all_trees = []

        for sentence in train:
            root = None
            root_id = None
            token_nodes = []
            for token in sentence:
                node = Tree(token.form, token.lemma, token.upos, token.xpos, token.deprel, form_dict,
                            lemma_dict, upos_dict, xpos_dict, deprel_dict, token.head)
                token_nodes.append(node)
                if token.deprel == 'root':
                    root = node
                    root_id = int(token.id)

            for token_id, token in enumerate(token_nodes):
                if token.parent == 0:
                    token.set_parent(None)
                else:
                    parent_id = int(token.parent) - 1
                    if token_id < parent_id:
                        token_nodes[parent_id].add_l_child(token)
                    elif token_id > parent_id:
                        token_nodes[parent_id].add_r_child(token)
                    else:
                        raise Exception('Root element should not be here!')
                    token.set_parent(token_nodes[parent_id])

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

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    (all_trees, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict) = create_trees(config)


    query_tree = decode_query('(' + config.get('settings', 'query') + ')')

    for tree in all_trees:
        # _, subtrees = tree.get_subtrees([query_tree], [])
        tree.r_children = []
        tree.l_children[1].l_children = []
        _, subtrees = tree.get_subtrees([{"l_children": [{'a1':''}, {'a2':''}], "r_children": []}, {"l_children": [{'b1':''}], "r_children": []}, {"l_children": [{'c1':''}, {'c2':''}, {'c3':''}], "r_children": []}], [])
        print('here')
        return


    # {"form": "", "lemma": "", "upos": "", "xpos": "", "l_children": [{}, {}], "r_children": [{}, {}]}
    # {"form": "", "lemma": "", "upos": "", "xpos": "", "l_children": [{}, {}], "r_children": [{}, {}]}

if __name__ == "__main__":
    main()
