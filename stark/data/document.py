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

class Document(object):
    def __init__(self):
        self.trees = []
        self.sentence_statistics = []
        self.form_dict = {}
        self.lemma_dict = {}
        self.upos_dict = {}
        self.xpos_dict = {}
        self.deprel_dict = {}
        self.misc_dict = {}

    def get_document_data(self):
        return [self.trees, self.form_dict, self.lemma_dict, self.upos_dict, self.xpos_dict, self.deprel_dict, self.misc_dict,
                self.sentence_statistics]

    @classmethod
    def create_document_from_cache(cls, doc_data):
        d = cls()
        d.trees, d.form_dict, d.lemma_dict, d.upos_dict, d.xpos_dict, d.deprel_dict, d.misc_dict, d.sentence_statistics = doc_data
        return d
