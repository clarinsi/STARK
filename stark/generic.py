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

import math
import sys


def create_output_string_form(tree):
    return tree.form.get_value()

def create_output_string_deprel(tree):
    return tree.deprel.get_value()

def create_output_string_lemma(tree):
    return tree.lemma.get_value() if tree.lemma.get_value() is not None else '_'

def create_output_string_upos(tree):
    return tree.upos.get_value()

def create_output_string_xpos(tree):
    return tree.xpos.get_value()

def create_output_string_feats(tree):
    return '|'.join([f'{k}={list(v.keys())[0]}' for k, v in tree.feats_detailed.items()])

def generate_key(node, create_output_strings, print_lemma=True):
    array = [[create_output_string(node) for create_output_string in create_output_strings]]
    if create_output_string_lemma in create_output_strings and print_lemma:
        key_array = [[create_output_string(
            node) if create_output_string != create_output_string_lemma else 'L=' + create_output_string(node) for
                      create_output_string in create_output_strings]]
    else:
        key_array = array
    if len(array[0]) > 1:
        key = '&'.join(key_array[0])
    else:
        key = key_array[0][0]

    return array, key

def generate_name(node, create_output_strings, print_lemma=True):
    array = [create_output_string(node) for create_output_string in create_output_strings]
    if create_output_string_lemma in create_output_strings and print_lemma:
        name_array = [create_output_string(
            node) if create_output_string != create_output_string_lemma else 'L=' + create_output_string(node) for
                      create_output_string in create_output_strings]
    else:
        name_array = array
    if len(array) > 1:
        name = '&'.join(name_array)
    else:
        name = name_array[0]

    return array, name

def get_collocabilities(ngram, unigrams_dict, corpus_size):
    sum_fwi = 0.0
    mul_fwi = 1.0
    for key_array in ngram['object'].array:
        # create key for unigrams
        if len(key_array) > 1:
            key = '&'.join(key_array)
        else:
            key = key_array[0]
        sum_fwi += unigrams_dict[key]
        mul_fwi *= unigrams_dict[key]

    if mul_fwi < 0:
        mul_fwi = sys.maxsize

    # number of all words
    N = corpus_size

    # n of ngram
    n = len(ngram['object'].array)
    O = ngram['number']
    E = mul_fwi / pow(N, n-1)

    # ['MI', 'MI3', 'Dice', 'logDice', 't-score', 'simple-LL']
    mi = math.log(O / E, 2)
    mi3 = math.log(pow(O, 3) / E, 2)
    dice = n * O / sum_fwi
    logdice = 14 + math.log(dice, 2)
    tscore = (O - E) / math.sqrt(O)
    simplell = 2 * (O * math.log10(O / E) - (O - E))
    return ['%.4f' % mi, '%.4f' % mi3, '%.4f' % dice, '%.4f' % logdice, '%.4f' % tscore, '%.4f' % simplell]
