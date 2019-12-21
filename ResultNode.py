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

from generic import generate_key, generate_name


class ResultNode(object):
    def __init__(self, node, architecture_order, create_output_strings):
        self.name_parts, self.name = generate_name(node, create_output_strings)
        # self.key_free = self.key
        # self.array = [[output_string]]
        # self.order_key = str(architecture_order)
        self.location = architecture_order
        self.deprel = node.deprel.get_value()
        # order with original numbers in sentences
        # self.order = str([architecture_order])
        # order with numbers from 0 to n of n-gram
        # self.root = ''
        # self.final_order = ''
        # self.separators = []

    def __repr__(self):
        return self.name