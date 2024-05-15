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
import string
import networkx as nx
from networkx.algorithms.bipartite import hopcroft_karp_matching

from stark.data.representation.tree import RepresentationTree
from stark.processing.filters import Filter


class GreedyRepresentationTree(RepresentationTree):
    def __init__(self, node, children, filters):
        self.tree_size = children[0]
        if filters['node_order']:
            children_sorted = children[1]
        else:
            children_sorted = sorted(children[1], key=lambda x: x.get_key())
        super().__init__(node, children_sorted, filters)

    def check_query(self, query):
        # compares query and children lengths
        query_length = len(query['children']) if 'children' in query else 0
        if query_length != len(self.children):
            return False

        # does node comparisons
        filt = Filter.check_query_tree(query, self.node.form, self.node.lemma, self.node.upos, self.node.xpos,
                                       self.node.feats, self.node.deprel, self.children, self.filters)

        if not filt:
            return False

        if not self.children:
            return True

        # compares children with query nodes
        # creates nodes for graph children nodes go from 1 on and query children go from -1 back.
        children_nodes = list(range(1, query_length+1))
        query_children_nodes = list(range(-query_length, 0))
        edges = []
        for i, child in enumerate(self.children):
            for j, query_child in enumerate(query['children']):
                if child.check_query(query_child):
                    edges.append((i + 1, -j - 1))

        graph = nx.Graph()
        graph.add_nodes_from(children_nodes, bipartite=1)
        graph.add_nodes_from(query_children_nodes, bipartite=0)
        graph.add_edges_from(edges)

        # hopcroft-karp algorithm efficiently finds number of connections between
        connections = hopcroft_karp_matching(graph, children_nodes)
        return len(connections) == query_length * 2

    def pass_filter(self, query_trees):
        """
        Validator of filters for greedy counter.
        :return: True when representation tree passes all filters.
        """
        # tests tree size
        if query_trees:
            pass_query = False
            for query in query_trees:
                if self.check_query(query):
                    pass_query = True
            if not pass_query:
                return False
        return Filter.check_representation_tree(self)

    def _check_tree_size(self):
        """
        Checks whether tree size is within filter parameters.
        :return:
        """
        return self.filters['tree_size_range'][0] <= self.tree_size <= self.filters['tree_size_range'][-1]

    # def finalize_result(self):
    #     self._reset_params()
    #     if self.filters['ignored_labels']:
    #         self._ignore_nodes()
    #
    #     # create order letters
    #     order = self.get_order()
    #     self.order_ids = order.copy()
    #     order_letters = [''] * len(self.order)
    #     for i in range(len(order)):
    #         ind = order.index(min(order))
    #         order[ind] = 10000
    #         order_letters[ind] = string.ascii_uppercase[i]
    #     self.order = ''.join(order_letters)
    #     return self
