#!/usr/bin/env python
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

import csv
import json
import math
import os
import random
import string
from abc import abstractmethod
from pathlib import Path
import sys
from os import path
import urllib.parse
import logging

here = path.abspath(path.dirname(__file__))
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger('stark')


class Writer(object):
    def __init__(self, summary, other_summary, filters, configs):
        self.summary = summary
        self.other_summary = other_summary
        self.filters = filters
        self.configs = configs

    @abstractmethod
    def write(self):
        return

    def lines_generator(self):
        other_representation_trees = self.other_summary.representation_trees if self.other_summary else None
        other_corpus_size = self.other_summary.corpus_size if self.other_summary else None

        sorted_list = sorted(self.summary.representation_trees.items(), key=lambda x: x[1]['number'], reverse=True)

        with open(os.path.join(here, '../resources/codes_mapper.json'), 'r') as f:
            codes_mapper = json.load(f)
        path = Path(self.configs['input_path']).name
        lang = path.split('_')[0]
        corpus_name = path.split('_')[1].split('-')[0].lower() if len(path.split('_')) > 1 else 'unknown'
        corpus = codes_mapper[lang][corpus_name] if lang in codes_mapper and corpus_name in codes_mapper[lang] else None

        if self.configs['sentence_count_file']:
            self.write_sentence_count_file()

        if self.configs['detailed_results_file']:
            self.write_detailed_results_file()

        if self.filters['tree_size_range'][-1]:
            len_words = self.filters['tree_size_range'][-1]
        else:
            len_words = int(len(self.configs['query'].split(" ")) / 2 + 1)
        header = ["Tree"] + ["Node " + string.ascii_uppercase[i] + "-" + node_type for i in range(len_words) for
                             node_type in self.filters['node_types']] + ['Absolute frequency']
        header += ['Relative frequency']
        if self.filters['node_order']:
            header += ['Order']
        if self.configs['grew_match']:
            header += ['Grew-match query']
        if corpus and self.configs['grew_match']:
            header += ['Grew-match URL']
        if self.filters['node_order'] and self.configs['depsearch']:
            header += ['Depsearch tree query']
        if self.filters['nodes_number']:
            header += ['Number of nodes']
        if self.filters['print_root']:
            header += ['Head node']
        if self.filters['example']:
            header += ['Example']
        if self.filters['association_measures']:
            header += ['MI', 'MI3', 'Dice', 'logDice', 't-score', 'simple-LL']
        if self.configs['compare']:
            header += ['Absolute frequency in second treebank', 'Relative frequency in second treebank', 'LL',
                       'BIC', 'Log ratio', 'OR', '%DIFF']
        yield header

        if self.filters['lines_threshold']:
            sorted_list = sorted_list[:self.filters['lines_threshold']]

        # body
        for k, v in sorted_list:
            v['object'].get_array()
            relative_frequency = v['number'] * 1000000.0 / self.summary.corpus_size
            if self.filters['frequency_threshold'] and self.filters['frequency_threshold'] > v['number']:
                break
            words_only = [word_att for word in v['object'].array for word_att in word] + ['' for _ in range(
                (self.filters['tree_size_range'][-1] - len(v['object'].array)) * len(v['object'].array[0]))]
            key = v['object'].get_key()[1:-1] if v['object'].get_key()[0] == '(' and v['object'].get_key()[
                -1] == ')' else v['object'].get_key()
            grew_nodes, grew_links = v['object'].get_grew()
            location_mapper = v['object'].get_location_mapper()
            key_grew = self.get_grew(grew_nodes, grew_links, self.filters['node_types'], self.filters['node_order'],
                                     location_mapper, self.filters['dependency_type'],
                                     self.filters['complete_tree_type'])
            row = [key] + words_only + [str(v['number'])]
            row += ['%.1f' % relative_frequency]
            if self.filters['node_order']:
                row += [v['object'].order]
            if self.configs['grew_match']:
                row += [key_grew]
            if corpus and self.configs['grew_match']:
                url = f'http://universal.grew.fr/?corpus={corpus}&request={urllib.parse.quote(key_grew)}'
                row += [url]
            if self.filters['node_order'] and self.configs['depsearch']:
                row += [v['object'].get_key_sorted()[1:-1]]
            if self.filters['nodes_number']:
                row += ['%d' % len(v['object'].array)]
            if self.filters['print_root']:
                row += [v['object'].node.name]
            if self.filters['example']:
                random_sentence_position = int(len(v['sentence']) * random.random())
                row += [v['sentence'][random_sentence_position][1]]
            if self.filters['association_measures']:
                row += self.get_collocabilities(v, self.summary.unigrams, self.summary.corpus_size)
            if self.configs['compare']:
                other_abs_freq = other_representation_trees[k]['number'] if k in other_representation_trees else 0
                row += self.get_keyness(v['number'], other_abs_freq, self.summary.corpus_size, other_corpus_size)
            yield row

    def write_sentence_count_file(self):
        if os.path.exists(self.configs['sentence_count_file']):
            os.remove(self.configs['sentence_count_file'])
        with open(self.configs['sentence_count_file'], "a", newline="", encoding="utf-8") as wf:
            key_list = [k for k, v in self.summary.representation_trees.items()]
            header = ['Sentence_id'] + key_list
            wf.write('\t'.join(header) + '\n')
            for sentence in self.summary.samples:
                wf.write(sentence['id'] + '\t' + '\t'.join(
                    [str(sentence['count'][k]) if k in sentence['count'] else '0' for k in key_list]) + '\n')

    def write_detailed_results_file(self):
        if os.path.exists(self.configs['detailed_results_file']):
            os.remove(self.configs['detailed_results_file'])
        with open(self.configs['detailed_results_file'], "a", newline="", encoding="utf-8") as wf:
            for k, v in self.summary.representation_trees.items():
                for s in v['sentence']:
                    wf.write(k + '\t' + s[0] + '\t' + s[1] + '\n')

    @staticmethod
    def get_keyness(abs_freq_A, abs_freq_B, count_A, count_B):
        if abs_freq_B <= 0:
            abs_freq_B = 0.000000000000000001
        E1 = count_A * (abs_freq_A + abs_freq_B) / (count_A + count_B)
        E2 = count_B * (abs_freq_A + abs_freq_B) / (count_A + count_B)

        LL = 2 * ((abs_freq_A * math.log(abs_freq_A / E1)) + (
                    abs_freq_B * math.log(abs_freq_B / E2))) if abs_freq_B > 0 else 0
        BIC = LL - math.log(count_A + count_B) if abs_freq_B > 0 else 0
        log_ratio = math.log(((abs_freq_A / count_A) / (abs_freq_B / count_B)), 2) if abs_freq_B > 0 else 0
        OR = (abs_freq_A / (count_A - abs_freq_A)) / (abs_freq_B / (count_B - abs_freq_B)) if abs_freq_B > 0 else 0
        diff = (((abs_freq_A / count_A) * 1000000 - (abs_freq_B / count_B) * 1000000) * 100) / (
                    (abs_freq_B / count_B) * 1000000) if abs_freq_B > 0 else 0

        if abs_freq_B <= 0:
            return ['%.0f' % abs_freq_B, '%.1f' % (abs_freq_B * 1000000.0 / count_B), LL, BIC, log_ratio, OR, diff]
        return ['%.0f' % abs_freq_B, '%.1f' % (abs_freq_B * 1000000.0 / count_B), '%.2f' % LL, '%.2f' % BIC,
                '%.2f' % log_ratio, '%.2f' % OR, '%.2f' % diff]

    @staticmethod
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
        grew += '; '.join([f'{link[0]} -[{link_node[1].deprel}]-> {link[1]}' for link, link_node in
                           zip(link_result, links)]) if dependency_type else \
            '; '.join([f'{link[0]} -> {link[1]}' for link in link_result])
        grew += '; ' + '; '.join([f'{link[0]} {link[2]} {link[1]}' for link in order_result])

        if complete:
            without_statements = []
            for i, key in enumerate(node_result.keys()):
                without_statements.append(f'without {{{key} -> X{i}}}')

            return grew + '} ' + ' '.join(without_statements)
        return grew + '}'

    @staticmethod
    def get_collocabilities(ngram, unigrams, corpus_size):
        sum_fwi = 0.0
        mul_fwi = 1.0
        for key_array in ngram['object'].array:
            # create key for unigrams
            if len(key_array) > 1:
                key = '&'.join(key_array)
            else:
                key = key_array[0]
            sum_fwi += unigrams[key]
            mul_fwi *= unigrams[key]

        if mul_fwi < 0:
            mul_fwi = sys.maxsize

        # number of all words
        N = corpus_size

        # n of ngram
        n = len(ngram['object'].array)
        O = ngram['number']
        E = mul_fwi / pow(N, n - 1)

        # ['MI', 'MI3', 'Dice', 'logDice', 't-score', 'simple-LL']
        mi = math.log(O / E, 2)
        mi3 = math.log(pow(O, 3) / E, 2)
        dice = n * O / sum_fwi
        logdice = 14 + math.log(dice, 2)
        tscore = (O - E) / math.sqrt(O)
        simplell = 2 * (O * math.log10(O / E) - (O - E))
        return ['%.2f' % mi, '%.2f' % mi3, '%.2f' % dice, '%.2f' % logdice, '%.2f' % tscore, '%.2f' % simplell]


class TSVWriter(Writer):
    def __init__(self, *configs):
        super().__init__(*configs)

    def write(self):
        with open(self.configs['output'], "w", newline="", encoding="utf-8") as f:
            # header - use every second space as a split
            writer = csv.writer(f, delimiter='\t')
            for line in self.lines_generator():
                writer.writerow(line)


class ObjectWriter(Writer):
    def __init__(self, *configs):
        super().__init__(*configs)

    def write(self):
        return list(self.lines_generator())
