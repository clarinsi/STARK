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
import os
import time
from pathlib import Path

from stark.processing.cache import ProcessorCache
from stark.processing.counters import QueryCounter, GreedyCounter
from stark.processing.document_processor import DocumentProcessor

logger = logging.getLogger('stark')


class Processor(object):
    """
    A class that iterates over all documents and stores cumulative results.
    """
    def __init__(self, configs, filters):
        self.configs = configs
        self.filters = filters

    def run_dir(self, summary):
        """
        Runs processing for directories. When enabled, use caching.
        :param summary:
        :return:
        """
        processor_cache = ProcessorCache(self)
        summary = processor_cache.load_cache(summary)

        for path in sorted(Path(self.configs['input_path']).rglob('*.conllu')):
            summary = processor_cache.process_trees(path, summary)

        return summary

    def run(self, path, summary):
        """
        Run processing.
        :param path_list: List of paths to documents that need to be processed.
        :param summary: A collection of datapoints used for result generation.
        :return:
        summary: A collection of datapoints used for result generation.
        """
        start_exe_time = time.time()

        document_processor = DocumentProcessor(str(path), self)
        document = document_processor.form_trees(summary, self.configs)
        logger.info("Trees formed time:")
        logger.info("--- %s seconds ---" % (time.time() - start_exe_time))
        if self.configs['greedy_counter']:
            tree_counter = GreedyCounter(document, summary, self.filters, self.configs)
        else:
            tree_counter = QueryCounter(document, summary, self.filters, self.configs)
        tree_counter.run()
        summary.samples.extend(document.sentence_statistics)

        logger.info(f"{len(summary.representation_trees)} unique trees counted time (execution time):")
        logger.info("Trees counted time (execution time):")
        logger.info("--- %s seconds ---" % (time.time() - start_exe_time))

        return summary
