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
    def __init__(self):
        self.feats_dict = {}
        self.query_trees = None
        self.samples = []
        self.corpus_size = 0
        self.unigrams = {}
        self.representation_trees = {}

    def set_query_trees(self, query_trees):
        self.query_trees = query_trees

    def get_summary_data(self):
        return (self.representation_trees, self.unigrams, self.corpus_size, self.feats_dict,
                self.samples)

    @classmethod
    def create_summary_from_cache(cls, sum_data):
        s = cls()
        s.representation_trees, s.unigrams, s.corpus_size, s.feats_dict, s.samples = sum_data
        return s
