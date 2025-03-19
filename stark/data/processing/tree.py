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

from stark.utils import create_output_string_lemma


class Tree(object):
    def __init__(self, index, form, lemma, upos, xpos, deprel, head, feats_detailed, misc, document, summary):

        feats_dict = summary.feats_dict

        if not hasattr(self, 'feats'):
            self.feats_detailed = {}

        if form not in document.form_dict:
            document.form_dict[form] = form
        self.form = document.form_dict[form]
        if lemma not in document.lemma_dict:
            document.lemma_dict[lemma] = lemma
        self.lemma = document.lemma_dict[lemma]
        if upos not in document.upos_dict:
            document.upos_dict[upos] = upos
        self.upos = document.upos_dict[upos]
        if xpos not in document.xpos_dict:
            document.xpos_dict[xpos] = xpos
        self.xpos = document.xpos_dict[xpos]
        if deprel not in document.deprel_dict:
            document.deprel_dict[deprel] = deprel
        self.deprel = document.deprel_dict[deprel]
        for feat in feats_detailed.keys():
            if feat not in feats_dict:
                feats_dict[feat] = {}
            if next(iter(feats_detailed[feat])) not in feats_dict[feat]:
                feats_dict[feat][next(iter(feats_detailed[feat]))] = next(iter(feats_detailed[feat]))
            if feat not in self.feats_detailed:
                self.feats_detailed[feat] = {}
            self.feats_detailed[feat][next(iter(feats_detailed[feat]))] = (
                feats_dict)[feat][next(iter(feats_detailed[feat]))]

        self.feats = {k: list(v.keys())[0] for k, v in self.feats_detailed.items()}
        if misc not in document.misc_dict:
            document.misc_dict[misc] = misc
        self.misc = document.misc_dict[misc]

        self.parent = head
        self.children = []
        self.children_split = -1
        self.conll = None

        self.index = index

        # for caching answers to questions
        self.cache = {}

    def add_child(self, child):
        self.children.append(child)

    def set_parent(self, parent):
        self.parent = parent

    def get_unigrams(self, create_output_strings):
        unigrams = [Tree._generate_key(self, create_output_strings, print_lemma=False)[1]]
        for child in self.children:
            unigrams += child.get_unigrams(create_output_strings)
        return unigrams

    def add_conll_sentence(self, conll):
        self.conll = conll

    def get_root(self):
        """
        Get root of a node.
        :return:
        """
        root = self
        while root.parent is not None:
            root = root.parent

        return root

    @staticmethod
    def _generate_key(node, create_output_strings, print_lemma=True):
        array = [[create_output_string(node) for create_output_string in create_output_strings]]
        if create_output_string_lemma in create_output_strings and print_lemma:
            key_array = [[create_output_string(
                node) if create_output_string != create_output_string_lemma else create_output_string(node) for
                          create_output_string in create_output_strings]]
        else:
            key_array = array
        if len(array[0]) > 1:
            key = '&'.join(key_array[0])
        else:
            key = key_array[0][0]

        return array, key

