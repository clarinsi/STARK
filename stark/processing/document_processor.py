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

import logging
import pyconll

from stark.data.document import Document
from stark.data.processing.greedy_tree import GreedyTree
from stark.data.processing.query_tree import QueryTree
from stark.processing.cache import DocumentCache

logger = logging.getLogger('stark')


class DocumentProcessor(object):
    def __init__(self, path, processor):
        self.path = path
        self.processor = processor
        self.cache = DocumentCache(self, path)

    def form_trees(self, summary):
        return self.cache.create_trees(summary)

    def create_trees(self, summary):
        document = Document()

        train = pyconll.load_from_file(self.path)

        for sentence in train:
            root = None
            token_nodes = []
            tokens = []
            for token in sentence:
                if not token.id.isdigit():
                    continue

                token_form = token.form if token.form is not None else '_'
                token_deprel = token.deprel if self.processor.configs['label_subtypes'] \
                    else token.deprel.split(':')[0]
                if self.processor.configs['greedy_counter']:
                    node = GreedyTree(int(token.id), token_form, token.lemma, token.upos, token.xpos, token_deprel, token.head,
                                token.feats, document, summary)
                else:
                    node = QueryTree(int(token.id), token_form, token.lemma, token.upos, token.xpos, token_deprel,
                                      token.head,
                                      token.feats, document, summary)
                token_nodes.append(node)
                space_after = token.misc[
                                  'SpaceAfter'].pop() != 'No' if token.misc is not None and 'SpaceAfter' in token.misc \
                    else True
                tokens.append((token_form, space_after))
                if token_deprel == 'root':
                    root = node

                summary.corpus_size += 1
            document.sentence_statistics.append({'id': sentence.id, 'tokens': tokens, 'count': {}})
            for token_id, token in enumerate(token_nodes):
                if isinstance(token.parent, int) or token.parent == '':
                    root = None
                    logger.warning('No parent: ' + sentence.id)
                    break
                if int(token.parent) == 0:
                    token.set_parent(None)
                else:
                    parent_id = int(token.parent) - 1
                    if token_nodes[parent_id].children_split == -1 and token_id > parent_id:
                        token_nodes[parent_id].children_split = len(token_nodes[parent_id].children)
                    token_nodes[parent_id].add_child(token)
                    token.set_parent(token_nodes[parent_id])

            for token in token_nodes:
                if token.children_split == -1:
                    token.children_split = len(token.children)

            if root == None:
                logger.warning('No root: ' + sentence.id)
                continue
            document.trees.append(root)

        return document
