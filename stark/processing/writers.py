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
import hashlib
import json
import math
import os
import random
import shutil
import string
from abc import abstractmethod
from pathlib import Path
import sys
from os import path
import urllib.parse
import logging
from tqdm import tqdm

here = path.abspath(path.dirname(__file__))
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger('stark')


class Writer(object):
    """
    A class used for writing results.
    """
    def __init__(self, summary, other_summary, filters, configs):
        self.summary = summary
        self.other_summary = other_summary
        self.filters = filters
        self.configs = configs

    @abstractmethod
    def write(self):
        return

    def lines_generator(self):
        """
        A generator that returns lines in array form, that can be used for further processing.
        :return:
        """
        other_representation_trees = self.other_summary.representation_trees if self.other_summary else None
        other_corpus_size = self.other_summary.corpus_size if self.other_summary else None
        random_sentence_position = 0

        # skip elements that do not fit filters
        if self.filters['frequency_threshold'] or self.filters['display_size_range'][-1]:
            # reset summary_size because some elements will be skipped!
            self.summary.max_tree_size = 1
            sorted_list = []
            for k, v in self.summary.representation_trees.items():
                # skip words that do not fit display size (when it is given)
                if (self.filters['display_size_range'][-1] and not
                        self.filters['display_size_range'][0] <= len(v['word_array']) <=
                        self.filters['display_size_range'][-1]):
                    continue

                if self.filters['frequency_threshold'] and self.filters['frequency_threshold'] > v['number']:
                    continue
                if self.summary.max_tree_size < len(v['word_array']):
                    self.summary.max_tree_size = len(v['word_array'])
                sorted_list.append((k, v))
        else:
            sorted_list = self.summary.representation_trees.items()

        sorted_list = sorted(sorted_list, key=lambda x: (-x[1]['number'], x[0]))

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

        if self.configs['annodoc_example_dir'] and (self.configs['detailed_results_file'] or self.configs['example']):
            self.write_annodoc_files()

        if self.configs['annodoc_detailed_dir'] and self.configs['detailed_results_file']:
            self.write_annodoc_detailed_files()

        if self.filters['display_size_range'][-1]:
            if not self.configs['greedy_counter']:
                len_words = self.filters['display_size_range'][-1]
            else:
                len_words = min(self.filters['display_size_range'][-1], self.summary.max_tree_size)
        else:
            len_words = int(len(self.configs['query'].split(" ")) / 2 + 1)
        header = ["Tree"]
        if self.configs['node_info']:
            header += ["Node " + string.ascii_uppercase[i % 26] + str(int(i/26)) + "-" + node_type if i >= 26 else
                             "Node " + string.ascii_uppercase[i % 26] + "-" + node_type for i in range(len_words) for
                             node_type in self.filters['node_types']]
        header += ['Absolute frequency', 'Relative frequency']
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
        if self.filters['head_info']:
            header += ['Head node']
        if self.filters['example']:
            header += ['Example']
        if self.filters['annodoc']:
            header += ['Annodoc']
        if self.filters['association_measures']:
            header += ['MI', 'MI3', 'Dice', 'logDice', 't-score', 'simple-LL']
        if self.configs['compare']:
            header += ['Absolute frequency in second treebank', 'Relative frequency in second treebank', 'Ratio', 'LL',
                       'BIC', 'Log ratio', 'OR', '%DIFF']
        yield header

        if self.filters['lines_threshold']:
            sorted_list = sorted_list[:self.filters['lines_threshold']]

        # body
        for k, v in tqdm(sorted_list, desc='Writing'):
            literal_key = v['key']
            word_array = v['word_array']

            relative_frequency = v['number'] * 1000000.0 / self.summary.corpus_size
            words_only = [word_att for word in word_array for word_att in word] + ['' for _ in range(
                (len_words - len(word_array)) * len(word_array[0]))]
            key = literal_key[1:-1] if (len(literal_key) > 0 and literal_key[0] == '(' and literal_key[-1] == ')') else literal_key

            row = [key]
            if self.configs['node_info']:
                row += words_only
            row += [str(v['number']), '%.1f' % relative_frequency]
            if self.filters['node_order']:
                order_letters = v['order_letters']
                row += [order_letters]
            if self.configs['grew_match']:
                location_mapper = v['location']
                grew_nodes, grew_links = v['grew']
                key_grew = self.get_grew(grew_nodes, grew_links, self.filters['node_types'], self.filters['node_order'],
                                         location_mapper, self.filters['dependency_type'],
                                         self.filters['complete_tree_type'])
                row += [key_grew]
                if corpus:
                    url = f'http://universal.grew.fr/?corpus={corpus}&request={urllib.parse.quote(key_grew)}'
                    row += [url]
            if self.filters['node_order'] and self.configs['depsearch']:
                row += [v['key_sorted']]
            if self.filters['nodes_number']:
                row += ['%d' % len(word_array)]
            if self.filters['head_info']:
                row += [v['root_name']]
            if self.filters['example']:
                random_sentence_position = 0
                min_sentence_size = 100000
                final_row = [v['sentence'][random_sentence_position][1]]
                for i, s in enumerate(v['sentence']):
                    if s[3] < 15:
                        final_row = [s[1]]
                        random_sentence_position = i
                        break
                    elif s[3] < min_sentence_size:
                        final_row = [s[1]]
                        random_sentence_position = i
                        min_sentence_size = s[3]
                row += final_row
            if self.filters['annodoc'] and (self.configs['detailed_results_file'] or self.filters['example']):
                annodoc_dict = {'id': v['sentence'][random_sentence_position][0],'positions': v['sentence'][random_sentence_position][2][1],'subtree_hash': hashlib.sha1(k.encode('utf-8')).hexdigest()}
                annodoc_json = json.dumps(annodoc_dict)
                row += [annodoc_json]
            if self.filters['association_measures']:
                row += self.get_collocabilities(v, self.summary.unigrams, self.summary.corpus_size)
            if self.configs['compare']:
                other_abs_freq = other_representation_trees[k]['number'] if k in other_representation_trees else 0
                row += self.get_keyness(v['number'], other_abs_freq, self.summary.corpus_size, other_corpus_size)
            yield row

    def write_sentence_count_file(self):
        """
        Writes into sentence count file.
        :return:
        """
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
        """
        Writes into detailed results file.
        :return:
        """
        if os.path.exists(self.configs['detailed_results_file']):
            os.remove(self.configs['detailed_results_file'])
        with open(self.configs['detailed_results_file'], "a", newline="", encoding="utf-8") as wf:
            for k, v in self.summary.representation_trees.items():
                for s in v['sentence']:
                    wf.write(k + '\t' + s[0] + '\t' + s[1] + '\n')

    def write_annodoc_files(self):
        """
        Writes conllu files separated by examples.
        :return:
        """
        annodoc_dir = Path(self.configs['annodoc_example_dir'])
        if annodoc_dir.exists():
            shutil.rmtree(annodoc_dir, ignore_errors=True)
        annodoc_dir.mkdir()
        for k, v in self.summary.representation_trees.items():
            for s in v['sentence']:
                annodoc_path = Path(self.configs['annodoc_example_dir'], s[0])
                if not annodoc_path.exists():
                    with open(annodoc_path, "w", newline="",
                              encoding="utf-8") as wf:
                        wf.write(s[2][0])

    def write_annodoc_detailed_files(self):
        """
        Writes tsv files that contain hashes of subtrees in a name. Each file contains a list with sentence_id and
        positions of subtree in a sentence.
        :return:
        """
        annodoc_dir = Path(self.configs['annodoc_detailed_dir'])
        if annodoc_dir.exists():
            shutil.rmtree(annodoc_dir, ignore_errors=True)
        annodoc_dir.mkdir()
        for k, v in self.summary.representation_trees.items():
            path = hashlib.sha1(k.encode('utf-8')).hexdigest()
            annodoc_path = Path(self.configs['annodoc_detailed_dir'], path) # calculate hash?
            if not annodoc_path.exists():
                with open(annodoc_path, "w", newline="",
                          encoding="utf-8") as wf:
                    for s in v['sentence']:
                        wf.write(f'{str(s[0])}\t{str(s[2][1])}\n')

    @staticmethod
    def get_keyness(abs_freq_A, abs_freq_B, count_A, count_B):
        """
        Calculates keyness for statistic purposes.
        :param abs_freq_A:
        :param abs_freq_B:
        :param count_A:
        :param count_B:
        :return:
        """
        ratio = '%.2f' % ((abs_freq_A / count_A) / (abs_freq_B / count_B)) if abs_freq_B else 'NaN'
        if abs_freq_B <= 0:
            abs_freq_B = 0.000000000000000001
        E1 = count_A * (abs_freq_A + abs_freq_B) / (count_A + count_B)
        E2 = count_B * (abs_freq_A + abs_freq_B) / (count_A + count_B)

        LL = 2 * ((abs_freq_A * math.log(abs_freq_A / E1)) + (
                abs_freq_B * math.log(abs_freq_B / E2))) if abs_freq_B > 0 else 0
        BIC = LL - math.log(count_A + count_B) if abs_freq_B > 0 else 0
        log_ratio = math.log(((abs_freq_A / count_A) / (abs_freq_B / count_B)), 2) if abs_freq_B > 0 else 0
        if count_A == abs_freq_A or count_B == abs_freq_B:
            OR = 'NaN'
        else:
            OR = (abs_freq_A / (count_A - abs_freq_A)) / (abs_freq_B / (count_B - abs_freq_B)) if abs_freq_B > 0 else 0
            OR = '%.2f' % OR
        diff = (((abs_freq_A / count_A) * 1000000 - (abs_freq_B / count_B) * 1000000) * 100) / (
                (abs_freq_B / count_B) * 1000000) if abs_freq_B > 0 else 0

        if abs_freq_B <= 0:
            return ['%.0f' % abs_freq_B, '%.1f' % (abs_freq_B * 1000000.0 / count_B), ratio, LL, BIC, log_ratio, OR,
                    diff]
        return ['%.0f' % abs_freq_B, '%.1f' % (abs_freq_B * 1000000.0 / count_B), ratio, '%.2f' % LL,
                '%.2f' % BIC, '%.2f' % log_ratio, OR, '%.2f' % diff]

    @staticmethod
    def get_grew(nodes, links, node_types, node_order, location_mapper, dependency_type, complete):
        """
        Forms grew format for usage and comparison on external website.
        :param nodes:
        :param links:
        :param node_types:
        :param node_order:
        :param location_mapper:
        :param dependency_type:
        :param complete:
        :return:
        """
        assert nodes
        node_result = {}
        for node in nodes:
            node_result[location_mapper[node.location]] = []
            for node_type in node_types:
                if node_type == 'deprel':
                    node_result[location_mapper[node.location]].append(f'deprel={node.node.deprel}')
                elif node_type == 'lemma':
                    node_result[location_mapper[node.location]].append(f'lemma="{node.node.lemma}"')
                elif node_type == 'upos':
                    node_result[location_mapper[node.location]].append(f'upos={node.node.upos}')
                elif node_type == 'xpos':
                    node_result[location_mapper[node.location]].append(f'xpos={node.node.xpos}')
                elif node_type == 'generic':
                    node_result[location_mapper[node.location]].append(f'')
                elif node_type == 'feats':
                    for k, v in node.feats.items():
                        node_result[location_mapper[node.location]].append(f'{k}={v}')
                else:
                    node_result[location_mapper[node.location]].append(f'form="{node.node.form}"')
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
        grew += '; '.join([node_k + ' [' + ', '.join(v) + ']' for node_k, v in node_result.items()])
        if links:
            grew += '; '
            grew += '; '.join([f'{link[0]} -[{link_node[1].node.deprel}]-> {link[1]}' for link, link_node in
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
        """
        Calculates collocabilities.
        :param ngram:
        :param unigrams:
        :param corpus_size:
        :return:
        """
        # n of ngram
        n = len(ngram['word_array'])

        # collocabilities are supported for n <= 10
        if n > 10:
            return ['NaN'] * 6

        sum_fwi = 0.0
        mul_fwi = 1.0
        for key_array in ngram['word_array']:
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
    """
    A class that writes into TSV file.
    """
    def __init__(self, *configs):
        super().__init__(*configs)

    def write(self):
        with open(self.configs['output'], "w", newline="", encoding="utf-8") as f:
            # header - use every second space as a split
            writer = csv.writer(f, delimiter='\t')
            for line in self.lines_generator():
                writer.writerow(line)


class ObjectWriter(Writer):
    """
        A class that returns results in object.
        """
    def __init__(self, *configs):
        super().__init__(*configs)

    def write(self):
        return list(self.lines_generator())
