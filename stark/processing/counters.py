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

import random
from abc import abstractmethod
from multiprocessing import Pool


class Counter(object):
    def __init__(self, document, summary, filters):
        self.document = document
        self.summary = summary
        self.filters = filters

    def run(self):
        if self.filters['cpu_cores'] > 1:
            self.run_multiprocessor()
        else:
            self.run_single_processor()

    @abstractmethod
    def run_single_processor(self):
        return

    @abstractmethod
    def run_multiprocessor(self):
        return

    @staticmethod
    def get_unigrams(input_data):
        tree, filters = input_data
        return tree.get_unigrams(filters['create_output_string_functs'])

    @staticmethod
    def recreate_sentence(sentence, r):
        recreated_sentence = ''
        for token_i, token in enumerate(sentence['tokens']):
            if token_i + 1 in r.order_ids:
                letter_position = r.order_ids.index(token_i + 1)
                recreated_sentence += f'{r.order[letter_position]}[{token[0]}]'
            else:
                recreated_sentence += token[0]
            if token[1]:
                recreated_sentence += ' '
        return recreated_sentence


class QueryCounter(Counter):
    """
    Counter that generates only trees that fit query trees.
    """
    def __init__(self, *configs):
        super().__init__(*configs)

    def run_multiprocessor(self):
        with Pool(self.filters['cpu_cores']) as p:
            all_unigrams = p.map(self.get_unigrams,
                                 [(tree, self.filters) for tree in self.document.trees])
            for unigrams in all_unigrams:
                for unigram in unigrams:
                    if unigram in self.summary.unigrams:
                        self.summary.unigrams[unigram] += 1
                    else:
                        self.summary.unigrams[unigram] = 1

            all_subtrees = p.map(self.tree_calculations,
                                 [(tree, self.summary.query_trees, self.filters) for tree in self.document.trees])

            for subtrees, sentence in zip(all_subtrees, self.document.sentence_statistics):
                self.postprocess_query_results(subtrees, sentence)

    def run_single_processor(self):
        for tree, sentence in zip(self.document.trees, self.document.sentence_statistics):
            input_data = (tree, self.summary.query_trees, self.filters)
            if self.filters['association_measures']:
                unigrams = self.get_unigrams((tree, self.filters))
                for unigram in unigrams:
                    if unigram in self.summary.unigrams:
                        self.summary.unigrams[unigram] += 1
                    else:
                        self.summary.unigrams[unigram] = 1

            subtrees = self.tree_calculations(input_data)
            self.postprocess_query_results(subtrees, sentence)

    @staticmethod
    def tree_calculations(input_data):
        tree, query_trees, filters = input_data
        _, subtrees = tree.get_query_subtrees(query_trees, [], filters)
        return [subtree for query_results in subtrees for subtree in query_results]

    def postprocess_query_results(self, subtrees, sentence):
        for r in subtrees:
            if self.filters['ignored_labels']:
                r.get_array()
                if self.filters['tree_size_range'] and \
                        (len(r.array) > self.filters['tree_size_range'][-1] or len(r.array) <
                         self.filters['tree_size_range'][0]):
                    continue
            if self.filters['node_order']:
                key = r.get_key() + r.order
            else:
                key = r.get_key()
            if key in self.summary.representation_trees:
                if self.filters['detailed_results_file']:
                    recreated_sentence = self.recreate_sentence(sentence, r)
                    self.summary.representation_trees[key]['sentence'].append((sentence['id'],
                                                                               recreated_sentence))
                elif self.filters['example'] and random.random() < 1.0 - (
                        self.summary.representation_trees[key]['number'] /
                        (self.summary.representation_trees[key]['number'] + 1)):
                    recreated_sentence = self.recreate_sentence(sentence, r)
                    self.summary.representation_trees[key]['sentence'] = [(sentence['id'],
                                                                           recreated_sentence)]
                self.summary.representation_trees[key]['number'] += 1
            else:
                self.summary.representation_trees[key] = {'object': r, 'number': 1}

                # recreate example sentence with shown positions of subtree
                if self.filters['example'] or self.filters['detailed_results_file']:
                    recreated_sentence = self.recreate_sentence(sentence, r)
                    self.summary.representation_trees[key]['sentence'] = [(sentence['id'],
                                                                           recreated_sentence)]
            if self.filters['sentence_count_file']:
                if key in sentence['count']:
                    sentence['count'][key] += 1
                else:
                    sentence['count'][key] = 1


class GreedyCounter(Counter):
    """
    Counter that generates all trees and then filters them.
    """

    def __init__(self, *configs):
        super().__init__(*configs)

    def run_multiprocessor(self):
        with Pool(self.filters['cpu_cores']) as p:
            all_unigrams = p.map(self.get_unigrams,
                                 [(tree, self.filters) for tree in self.document.trees])
            for unigrams in all_unigrams:
                for unigram in unigrams:
                    if unigram in self.summary.unigrams:
                        self.summary.unigrams[unigram] += 1
                    else:
                        self.summary.unigrams[unigram] = 1

            all_subtrees = p.map(self.tree_calculations,
                                 [(tree, self.summary.query_trees, self.filters) for tree in self.document.trees])

            for subtrees, sentence in zip(all_subtrees, self.document.sentence_statistics):
                self.postprocess_query_results(subtrees, sentence)

    def run_single_processor(self):
        for tree, sentence in zip(self.document.trees, self.document.sentence_statistics):
            input_data = (tree, self.summary.query_trees, self.filters)
            if self.filters['association_measures']:
                unigrams = self.get_unigrams((tree, self.filters))
                for unigram in unigrams:
                    if unigram in self.summary.unigrams:
                        self.summary.unigrams[unigram] += 1
                    else:
                        self.summary.unigrams[unigram] = 1

            subtrees = self.tree_calculations(input_data)
            self.postprocess_query_results(subtrees, sentence)

    @staticmethod
    def tree_calculations(input_data):
        tree, query_trees, filters = input_data
        _, subtrees = tree.get_all_subtrees(filters)
        return [subtree.finalize_result() for subtree in subtrees]

    def postprocess_query_results(self, subtrees, sentence):
        for r in subtrees:
            if self.filters['ignored_labels']:
                r.get_array()
                if self.filters['tree_size_range'] and \
                        (len(r.array) > self.filters['tree_size_range'][-1] or len(r.array) <
                         self.filters['tree_size_range'][0]):
                    continue
            if self.filters['node_order']:
                key = r.get_key() + r.order
            else:
                key = r.get_key()
            if key in self.summary.representation_trees:
                if self.filters['detailed_results_file']:
                    recreated_sentence = self.recreate_sentence(sentence, r)
                    self.summary.representation_trees[key]['sentence'].append((sentence['id'],
                                                                               recreated_sentence))
                elif self.filters['example'] and random.random() < 1.0 - (
                        self.summary.representation_trees[key]['number'] /
                        (self.summary.representation_trees[key]['number'] + 1)):
                    recreated_sentence = self.recreate_sentence(sentence, r)
                    self.summary.representation_trees[key]['sentence'] = [(sentence['id'],
                                                                           recreated_sentence)]
                self.summary.representation_trees[key]['number'] += 1
            else:
                self.summary.representation_trees[key] = {'object': r, 'number': 1}

                # recreate example sentence with shown positions of subtree
                if self.filters['example'] or self.filters['detailed_results_file']:
                    recreated_sentence = self.recreate_sentence(sentence, r)
                    self.summary.representation_trees[key]['sentence'] = [(sentence['id'],
                                                                           recreated_sentence)]
            if self.filters['sentence_count_file']:
                if key in sentence['count']:
                    sentence['count'][key] += 1
                else:
                    sentence['count'][key] = 1
