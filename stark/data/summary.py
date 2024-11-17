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


class Summary(object):
    """
    A class that is used to store results of processing.
    """
    def __init__(self):
        self.feats_dict = {}
        self.query_trees = None
        self.samples = []
        self.corpus_size = 0
        self.unigrams = {}
        self.representation_trees = {}
        self.max_tree_size = 0

    def set_query_trees(self, query_trees):
        """
        A function that sets query trees when they are needed.
        :param query_trees:
        :return:
        """
        self.query_trees = query_trees

    def get_summary_data(self):
        """
        A function that returns summary data used for storing cache.
        :return:
        """
        return (self.representation_trees, self.unigrams, self.corpus_size, self.feats_dict,
                self.samples, self.max_tree_size, self.query_trees)

    @classmethod
    def create_summary_from_cache(cls, sum_data):
        """
        A function that forms summary from cache.
        :param sum_data:
        :return:
        """
        s = cls()
        s.representation_trees, s.unigrams, s.corpus_size, s.feats_dict, s.samples, s.max_tree_size, s.query_trees = (
            sum_data)
        return s

    # def get_size_representation_trees(self):
    #     size = 0
    #     for represetation_tree_k, represetation_tree_v in self.representation_trees.items():
    #         size += sys.getsizeof(represetation_tree_k)
    #         size += sys.getsizeof(represetation_tree_v['number'])
    #         size += sys.getsizeof(represetation_tree_v['object'])
    #         size += represetation_tree_v['object'].get_size()
    #
    #     return size
