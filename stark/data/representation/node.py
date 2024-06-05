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


class RepresentationNode(object):
    def __init__(self, node, architecture_order, create_output_strings):
        self.name_parts, self.name = self.generate_name(node, create_output_strings)
        self.location = architecture_order
        self.node = node
        for k, v in node.feats_detailed.items():
            assert len(v.keys()) == 1

        self.feats = {k: list(v.keys())[0] for k, v in node.feats_detailed.items()}

    def __repr__(self):
        return self.name

    @staticmethod
    def generate_name(node, create_output_strings, print_lemma=True):
        array = [create_output_string(node) for create_output_string in create_output_strings]
        if create_output_string_lemma in create_output_strings and print_lemma:
            name_array = [create_output_string(
                node) if create_output_string != create_output_string_lemma else create_output_string(node) for
                          create_output_string in create_output_strings]
        else:
            name_array = array
        if len(array) > 1:
            name = '&'.join(name_array)
        else:
            name = name_array[0]

        return array, name
