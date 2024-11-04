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

import hashlib
import os

import logging
from pathlib import Path

from stark.data.document import Document
from stark.data.summary import Summary
from stark.utils import load_zipped_pickle, save_zipped_pickle

logger = logging.getLogger('stark')


class ProcessorCache(object):
    """
    Caching class, used as a wrapper for processing multiple files. It enables continuation processing.
    """
    def __init__(self, processor):
        self.configs = processor.configs
        self.already_processed = set()
        self._checkpoint_path = Path(self.configs['internal_saves'], 'checkpoint.pkl') \
            if self.configs['internal_saves'] is not None else None
        self.processor = processor

    def load_cache(self, summary):
        """
        Loads cache when applicable and deletes it if needed.
        :return:
        summary: Either received summary or loaded one.
        """
        if (self._checkpoint_path is None or not self._checkpoint_path.exists() or
                not self.configs['continuation_processing']):
            if self._checkpoint_path is not None and self._checkpoint_path.exists():
                os.remove(self._checkpoint_path)
        else:
            return self._load_cache()
        return summary

    def _load_cache(self):
        """
        Actually loads cache.
        :return:
        summary: Loaded summary
        """
        self.already_processed, summary_data = load_zipped_pickle(self._checkpoint_path)
        summary = Summary.create_summary_from_cache(summary_data)
        return summary

    def _save_cache(self, summary):
        """
        Actually saves cache.
        :return:
        """
        summary_data = summary.get_summary_data()
        save_zipped_pickle(
            (self.already_processed, summary_data),
            self._checkpoint_path, protocol=2)

    def process_trees(self, path, summary):
        """
        Skips documents that were already processed and stores processed results in cache.
        :param summary: Processing summary.
        :param path: Path to dir.
        :return:
        summary: A collection of datapoints used for result generation.
        """
        if str(path) in self.already_processed:
            logger.info(f'Skipping: {str(path)}')
            return summary

        summary = self.processor.run(path, summary)
        self.already_processed.add(str(path))
        if self._checkpoint_path:
            self._save_cache(summary)

        return summary


class DocumentCache(object):
    """
    Cache that stores generated sentence trees from files. When used, reading input files is not necessary anymore.
    May be problematic if users modify input files and don't rename them.
    """
    def __init__(self, document_processor, path):
        configs = document_processor.processor.configs
        self.document_processor = document_processor
        self.path = path
        self._internal_file = os.path.join(configs['internal_saves'], hashlib.sha1(path.encode('utf-8')).hexdigest()) \
            if configs['internal_saves'] is not None else None
        # do not save cache if input is dir
        self._save = not os.path.isdir(configs['input_path'])

    def create_trees(self, summary, configs):
        if self._internal_file is None or not os.path.exists(self._internal_file) or not self._save:
            document = self.document_processor.create_trees(summary, configs)

            if self._internal_file is not None and self._save:
                self._save_cache(document, summary)
        else:
            document = self._load_cache(summary)

        return document

    def _save_cache(self, document, summary):
        document_data = document.get_document_data() + [summary.corpus_size, summary.feats_dict]
        save_zipped_pickle(document_data, self._internal_file, protocol=2)

    def _load_cache(self, summary):
        document_data = load_zipped_pickle(self._internal_file)
        summary.corpus_size, summary.feats_dict = document_data[-2:]
        return Document.create_document_from_cache(document_data[:-2])
