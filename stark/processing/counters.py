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
from tqdm import tqdm


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

    @staticmethod
    @abstractmethod
    def tree_calculations(input_data):
        return []

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

            i = 0
            with tqdm(desc='Creating subtrees', total=len(self.document.trees)) as pbar:
                for subtrees in p.imap(self.tree_calculations,
                                                [(tree, self.summary.query_trees, self.filters) for tree in self.document.trees]):

                    for subtree in subtrees:
                        self.postprocess_query_results(subtree, self.document.sentence_statistics[i])
                    i += 1
                    pbar.update()

    def run_single_processor(self):
        for tree, sentence in tqdm(zip(self.document.trees, self.document.sentence_statistics), desc='Processing',
                                   total=len(self.document.trees)):
            input_data = (tree, self.summary.query_trees, self.filters)
            if self.filters['association_measures']:
                unigrams = self.get_unigrams((tree, self.filters))
                for unigram in unigrams:
                    if unigram in self.summary.unigrams:
                        self.summary.unigrams[unigram] += 1
                    else:
                        self.summary.unigrams[unigram] = 1

            subtrees = self.tree_calculations(input_data)
            for subtree in subtrees:
                self.postprocess_query_results(subtree, sentence)

    @staticmethod
    def get_unigrams(input_data):
        tree, filters = input_data
        return tree.get_unigrams(filters['create_output_string_functs'])

    def recreate_sentence(self, sentence, r):
        recreated_sentence = ''
        for token_i, token in enumerate(sentence['tokens']):
            order = r.get_order(self.filters)
            if token_i + 1 in order:
                letter_position = order.index(token_i + 1)
                order_letters = r.get_order_letters(order)
                recreated_sentence += f'{order_letters[letter_position]}[{token[0]}]'
            else:
                recreated_sentence += token[0]
            if token[1]:
                recreated_sentence += ' '
        return recreated_sentence

    def postprocess_query_results(self, r, sentence):
        # for r in subtrees:
        if self.filters['ignored_labels']:
            key, word_array = r.get_key_array(self.filters)
            if self.filters['tree_size_range'] and \
                    (len(word_array) > self.filters['tree_size_range'][-1] or len(word_array) <
                     self.filters['tree_size_range'][0]):
                return
        else:
            key = r.get_key(self.filters)
        if self.filters['node_order']:
            order_letters = r.get_order_letters(r.get_order(self.filters))
            key = key + order_letters
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


class QueryCounter(Counter):
    """
    Counter that generates only trees that fit query trees.
    """
    def __init__(self, *configs):
        super().__init__(*configs)

    @staticmethod
    def tree_calculations(input_data):
        tree, query_trees, filters = input_data
        _, subtrees = tree.get_subtrees(query_trees, [], filters)
        return [subtree for query_results in subtrees for subtree in query_results]


class GreedyCounter(Counter):
    """
    Counter that generates all trees and then filters them.
    """

    def __init__(self, *configs):
        super().__init__(*configs)

    @staticmethod
    def tree_calculations(input_data):
        tree, query_trees, filters = input_data
        _, subtrees = tree.get_subtrees(filters)
        subtrees = GreedyCounter.filter_subtrees(query_trees, subtrees, filters)
        return subtrees

    @staticmethod
    def filter_subtrees(query_trees, subtrees, filters):
        subtrees = [subtree for subtree in subtrees if subtree.pass_filter(query_trees, filters)]
        subtrees = [subtree.ignore_labels(filters) for subtree in subtrees]
        return subtrees
