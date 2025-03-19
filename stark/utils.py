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

import gzip
import pickle
import re
from pathlib import Path


def save_zipped_pickle(obj, filename, protocol=-1):
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(filename, 'wb') as f:
        pickle.dump(obj, f, protocol)


def load_zipped_pickle(filename):
    with gzip.open(filename, 'rb') as f:
        loaded_object = pickle.load(f)
        return loaded_object


def printable_answers(query):
    all_orders = re.split(r"\s+(?=[^()]*(?:\(|$))", query)
    node_actions = all_orders[::2]

    if len(node_actions) > 1:
        res = []
        for node_action in node_actions:
            # if command in bracelets remove them and treat command as new query
            if not node_action:
                res.extend(['('])
            elif node_action[0] == '(' and node_action[-1] == ')':
                res.extend(printable_answers(node_action[1:-1]))
            else:
                res.extend([node_action])
        return res
    else:
        return [query]


def create_output_string_form(tree):
    return tree.form


def create_output_string_deprel(tree):
    return tree.deprel


def create_output_string_lemma(tree):
    return tree.lemma if tree.lemma is not None else '_'


def create_output_string_upos(tree):
    return tree.upos


def create_output_string_xpos(tree):
    return tree.xpos


def create_output_string_none(tree):
    return '_'


def create_output_string_feats(tree):
    return '|'.join([f'{k}={list(v.keys())[0]}' for k, v in tree.feats_detailed.items()])


def create_output_string_misc(tree):
    return tree.misc
