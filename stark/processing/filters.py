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

from stark.utils import create_output_string_deprel, create_output_string_lemma, create_output_string_upos, \
    create_output_string_xpos, create_output_string_feats, create_output_string_form


def read_filters(configs):
    tree_size = configs['tree_size']
    tree_size_range = tree_size.split('-')
    tree_size_range = [int(r) for r in tree_size_range]

    # set filters
    node_type = configs['node_type']
    node_types = node_type.split('+')
    create_output_string_functs = []
    for node_type in node_types:
        assert node_type in ['deprel', 'lemma', 'upos', 'xpos', 'form', 'feats'], '"node_type" is not set up correctly'
        if node_type == 'deprel':
            create_output_string_funct = create_output_string_deprel
        elif node_type == 'lemma':
            create_output_string_funct = create_output_string_lemma
        elif node_type == 'upos':
            create_output_string_funct = create_output_string_upos
        elif node_type == 'xpos':
            create_output_string_funct = create_output_string_xpos
        elif node_type == 'feats':
            create_output_string_funct = create_output_string_feats
        else:
            create_output_string_funct = create_output_string_form
        create_output_string_functs.append(create_output_string_funct)

    filters = {
        'create_output_string_functs': create_output_string_functs,
        'node_types': node_types,
        'tree_size_range': tree_size_range,
        'cpu_cores': configs['cpu_cores'],
        'internal_saves': configs['internal_saves'],
        'input': configs['input_path'],
        'node_order': configs['node_order'],
        'dependency_type': configs['dependency_type'],
        'label_whitelist': configs['label_whitelist'],
        'ignored_labels': configs['ignored_labels'],
        'example': configs['example'],
        'sentence_count_file': configs['sentence_count_file'],
        'detailed_results_file': configs['detailed_results_file'],
        'complete_tree_type': configs['complete_tree_type'],
        'association_measures': configs['association_measures'],
        'nodes_number': configs['nodes_number'],
        'frequency_threshold': configs['frequency_threshold'],
        'lines_threshold': configs['lines_threshold'],
        'print_root': configs['print_root']
    }

    if configs['root_whitelist']:
        # test
        filters['root_whitelist'] = []

        for option in configs['root_whitelist']:
            attribute_dict = {}
            for attribute in option.split('&'):
                value = attribute.split('=')
                if len(value) == 1:
                    attribute_dict['form'] = value[0]
                else:
                    attribute_dict[value[0]] = value[1]
            filters['root_whitelist'].append(attribute_dict)
    else:
        filters['root_whitelist'] = []

    return filters
