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

from stark.data.processing.tree import Tree
from stark.data.representation.greedy_tree import GreedyRepresentationTree
from stark.data.representation.node import RepresentationNode
from stark.processing.filters import Filter


class GreedyTree(Tree):
    def __init__(self, index, form, lemma, upos, xpos, deprel, head, feats_detailed, token_misc, document, summary):
        super().__init__(index, form, lemma, upos, xpos, deprel, head, feats_detailed, token_misc, document, summary)

    @staticmethod
    def _processing_filter(combinations, child_active_tree, filters):
        """
        Utilizes loose filters that might improve greedy performance (ie. tree_size).
        :param combinations: List containing previous children combinations.
        :param child_active_tree: A child to be added to combinations if it passes filters.
        :param filters:
        :return:
        """
        # checks whether tree size is not too high
        # checks if label is in white list (if such a list exists)
        return (combinations[0] + child_active_tree.tree_size <= filters['tree_size_range'][-1] and
                Filter.check_label_whitelist(child_active_tree.node.node.deprel, filters))

    @staticmethod
    def _merge_incomplete_combinations(combinations, child_active_trees, filters):
        """
        Creates all possible combinations of children trees when complete_tree_type=no. It utilizes loose processing
        filters.
        :param combinations: A list of all combinations of a tree node.
        :param child_active_trees: A list of trees that contain child node.
        :param filters:
        :return:
        """
        # create all viable children combinations
        new_active_trees = []

        for child_active_tree in child_active_trees:
            for combination in combinations:
                if GreedyTree._processing_filter(combination, child_active_tree, filters):
                    new_active_trees.append((combination[0] + child_active_tree.tree_size,
                                             combination[1] + [child_active_tree]))

        combinations.extend(new_active_trees)
        return combinations

    @staticmethod
    def _merge_complete_combinations(combinations, child_active_trees, filters):
        """
        Creates all possible combinations of children trees when complete_tree_type=yes. Always generates all complete
        trees (there are fairly few of them) - no filtering!
        :param combinations:
        :param child_active_trees:
        :return:
        """
        if not child_active_trees or not combinations or not GreedyTree._processing_filter(combinations[0], child_active_trees[0], filters):
            return []
        new_combinations_size = combinations[0][0] + child_active_trees[0].tree_size
        combinations[0][1].append(child_active_trees[0])
        combinations[0] = (new_combinations_size, combinations[0][1])
        return combinations

    @staticmethod
    def _merge_combinations(combinations, child_active_trees, filters):
        """
        Creates all possible combinations of children trees.
        :param combinations: A list of all combinations of a tree node.
        :param child_active_trees: A list of trees that contain child node.
        :param filters:
        :return:
        """
        if filters['complete_tree_type']:
            combinations = GreedyTree._merge_complete_combinations(combinations, child_active_trees, filters)
        else:
            combinations = GreedyTree._merge_incomplete_combinations(combinations, child_active_trees, filters)

        return combinations

    def get_subtrees(self, filters):
        """
        A recursion that builds representation trees (representation_tree) and stores and collect them (trees).
        :param filters:
        :return:
        """
        # a list that stores all trees
        trees = []
        # A tuple containing cumulative size of all children, coupled with a list of children combinations.
        # The list contains combinations that are connected to the current node (and are relevant for further
        # generation). Set to [[]] because you always want an empty tree containing only itself.
        combinations = [(1, [])]

        node = RepresentationNode(self, self.index, filters['create_output_string_functs'])
        for child in self.children:
            child_active_trees, child_trees = child.get_subtrees(filters)
            combinations = GreedyTree._merge_combinations(combinations, child_active_trees, filters)
            trees.extend(child_trees)

        active_trees = []
        for combination in combinations:
            active_trees.append(GreedyRepresentationTree(node, combination, filters))
        trees.extend(active_trees)
        return active_trees, trees
