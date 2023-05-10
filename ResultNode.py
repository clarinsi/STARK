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
        self.location = architecture_order
        self.deprel = node.deprel.get_value()
        self.form = node.form.get_value()
        self.lemma = node.lemma.get_value()
        self.upos = node.upos.get_value()
        self.xpos = node.xpos.get_value()
        for k, v in node.feats_detailed.items():
            assert len(v.keys()) == 1

        self.feats = {k: list(v.keys())[0] for k, v in node.feats_detailed.items()}

    def __repr__(self):
        return self.name
