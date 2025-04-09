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
import gc
import logging
import os

import pyconll

from stark.data.document import Document
from stark.data.processing.greedy_tree import GreedyTree
from stark.data.processing.query_tree import QueryTree
from stark.processing.cache import DocumentCache

logger = logging.getLogger('stark')


class DocumentProcessor(object):
    """
    A class that processes document.
    """
    def __init__(self, path, processor):
        self.path = path
        self.processor = processor
        self.cache = DocumentCache(self, path)

    def form_trees(self, summary, configs):
        """
        Forms trees by trying to load it from cache or processing it.
        :param summary:
        :return:
        """
        return self.cache.create_trees(summary, configs)

    @staticmethod
    def _reform_misc(misc):
        """
        Uses pyconll to reform misc column from dict created by the same library

        :param misc:
        :return:
        """
        return pyconll.unit.token._dict_mixed_conll_map(misc, '_', '|',
                                                 '=', ',',
                                                 lambda pair: pair[0].lower())

    def create_trees(self, summary, configs):
        """
        Creates trees based on configs and stores them in Document object.
        :param configs:
        :param summary:
        :return:
        """
        document = Document()

        logger.info("Reading file: " + self.path)
        train = pyconll.load_from_file(self.path)
        for sentence in train:
            token_nodes = []
            tokens = []
            for token in sentence:
                if not token.id.isdigit():
                    continue

                token_form = token.form if token.form is not None else '_'
                token_lemma = token.lemma if token.lemma is not None else '_'
                token_upos = token.upos if token.upos is not None else '_'
                token_xpos = token.xpos if token.xpos is not None else '_'
                token_misc = self._reform_misc(token.misc) if token.misc else '_'
                token_deprel = token.deprel if self.processor.configs['label_subtypes'] \
                    else token.deprel.split(':')[0]
                if self.processor.configs['greedy_counter']:
                    node = GreedyTree(int(token.id), token_form, token_lemma, token_upos, token_xpos, token_deprel,
                                      token.head, token.feats, token_misc, document, summary)
                else:
                    node = QueryTree(int(token.id), token_form, token_lemma, token_upos, token_xpos, token_deprel,
                                     token.head, token.feats, token_misc, document, summary)
                token_nodes.append(node)
                space_after = token.misc[
                                  'SpaceAfter'].pop() != 'No' if token.misc is not None and 'SpaceAfter' in token.misc \
                    else True
                tokens.append((token_form, space_after))

                summary.corpus_size += 1
            document.sentence_statistics.append({'id': sentence.id, 'tokens': tokens, 'count': {}})
            roots = []
            for token_id, token in enumerate(token_nodes):
                if isinstance(token.parent, int) or token.parent == '':
                    logger.warning('No parent: ' + sentence.id)
                    break
                if int(token.parent) == 0:
                    token.set_parent(None)
                    # add a conllu string if necessary
                    if configs['annodoc_example_dir'] is not None:
                        token.add_conll_sentence(sentence.conll())
                    roots.append(token)
                else:
                    parent_id = int(token.parent) - 1
                    if token_nodes[parent_id].children_split == -1 and token_id > parent_id:
                        token_nodes[parent_id].children_split = len(token_nodes[parent_id].children)
                    token_nodes[parent_id].add_child(token)
                    token.set_parent(token_nodes[parent_id])

            for token in token_nodes:
                if token.children_split == -1:
                    token.children_split = len(token.children)

            if not roots:
                logger.warning('No root: ' + sentence.id)

            document.trees.append(roots)

        del train
        gc.collect()

        return document
