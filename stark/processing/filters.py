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
    create_output_string_xpos, create_output_string_feats, create_output_string_form, create_output_string_none, \
    create_output_string_misc

ROOT_WHITELIST_OPTIONS = ['deprel', 'feats', 'form', 'lemma', 'upos', 'misc']


def read_filters(configs):
    """
    Prepares filters for faster execution.
    :param configs:
    :return:
    """
    tree_size = configs['tree_size']
    tree_size_range = tree_size.split('-')
    tree_size_range = [int(r) for r in tree_size_range]

    display_size = configs['display_size']
    display_size_range = display_size.split('-')
    display_size_range = [int(r) for r in display_size_range]

    # set filters
    node_type = configs['node_type']
    if node_type:
        node_types = node_type.split('+')
        create_output_string_functs = []
        for node_type in node_types:
            assert node_type in ['deprel', 'lemma', 'upos', 'xpos', 'form', 'feats', 'misc'], \
                '"node_type" is not set up correctly'
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
            elif node_type == 'misc':
                create_output_string_funct = create_output_string_misc
            else:
                create_output_string_funct = create_output_string_form
            create_output_string_functs.append(create_output_string_funct)
    else:
        create_output_string_functs = [create_output_string_none]
        node_types = ['generic']

    filters = {
        'create_output_string_functs': create_output_string_functs,
        'node_types': node_types,
        'tree_size_range': tree_size_range,
        'display_size_range': display_size_range,
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
        'annodoc': configs['annodoc_example_dir'],
        'complete_tree_type': configs['complete_tree_type'],
        'association_measures': configs['association_measures'],
        'nodes_number': configs['nodes_number'],
        'frequency_threshold': configs['frequency_threshold'],
        'lines_threshold': configs['lines_threshold'],
        'head_info': configs['head_info']
    }

    if configs['root_whitelist']:
        filters['root_whitelist'] = []

        for option in configs['root_whitelist']:
            attribute_dict = {}
            for attribute in option.split('&'):
                value = attribute.split('=')
                value[1] = '='.join(attribute.split('=')[1:])
                # look for negation sign, if there is only one character - ! it will search for form ! instead
                if value[0][0] == '!' and len(value[0]) > 1:
                    negation = True
                    value[0] = value[0][1:]
                else:
                    negation = False
                if len(value) == 1:
                    attribute_dict['form'] = (negation, value[0])
                else:
                    attribute_dict[value[0]] = (negation, value[1])
            filters['root_whitelist'].append(attribute_dict)
    else:
        filters['root_whitelist'] = []

    return filters


class Filter(object):
    @staticmethod
    def check_representation_tree(tree, filters):
        """
        Checks if greedy representation tree passes filters.
        :param filters:
        :param tree:
        :return:
        """
        return (
                Filter.check_tree_size(tree.tree_size, filters)
                and Filter.check_root_whitelist(tree.node.node.form, tree.node.node.lemma, tree.node.node.upos,
                                                tree.node.node.feats, tree.node.node.deprel, tree.node.node.misc, filters)
        )

    @staticmethod
    def check_query_tree(query_tree, form, lemma, upos, xpos, feats, deprel, children, filters):
        """
        Checks if attributes of a tree fit attributes of query_tree.
        :param query_tree:
        :param form:
        :param lemma:
        :param upos:
        :param xpos:
        :param feats:
        :param deprel:
        :param children:
        :param filters:
        :return:
        """
        filter_passed = (not filters['complete_tree_type'] or (len(children) == 0 and 'children' not in query_tree) or
                         ('children' in query_tree and len(children) == len(query_tree['children'])))

        # restrictions might not be in query tree when dealing with query counter and size
        if 'restrictions' not in query_tree or not query_tree['restrictions']:
            return filter_passed

        # ('deprel' not in option or (option['deprel'][1] == deprel) == (not option['deprel'][0])) and \
        for option in query_tree['restrictions']:
            filter_passed = ('form' not in option or (option['form'][1] == form) == (not option['form'][0])) and \
                ('lemma' not in option or (option['lemma'][1] == lemma) == (not option['lemma'][0])) and \
                ('upos' not in option or (option['upos'][1] == upos) == (not option['upos'][0])) and \
                ('xpos' not in option or (option['xpos'][1] == xpos) == (not option['xpos'][0])) and \
                ('deprel' not in option or (option['deprel'][1] == deprel) == (not option['deprel'][0])) and \
                Filter._check_query_tree_feats(option, feats)

            if filter_passed:
                return True

        return False

    @staticmethod
    def _check_query_tree_feats(option, feats):
        """
        Checks if feats of a tree fit feats of option.
        :param option:
        :param feats:
        :return:
        """
        if 'feats_detailed' not in option:
            return True

        for feat in option['feats_detailed'].keys():
            if feat not in feats:
                if not option['feats_detailed'][feat][0]:
                    return False
            elif option['feats_detailed'][feat][1] != feats[feat] and not option['feats_detailed'][feat][0]:
                return False
            elif option['feats_detailed'][feat][1] == feats[feat] and option['feats_detailed'][feat][0]:
                return False
        return True

    @staticmethod
    def check_tree_size(size, filters):
        """
        Checks if tree size is in filtered range.
        :param size:
        :param filters:
        :return:
        """
        return filters['tree_size_range'][0] <= size <= filters['tree_size_range'][-1]

    @staticmethod
    def check_root_whitelist(form, lemma, upos, feats, deprel, misc, filters):
        """
        When root whitelist exists checks if element parameters are acceptable.
        :param form:
        :param lemma:
        :param upos:
        :param feats:
        :param deprel:
        :param filters:
        :return:
        """
        if not filters['root_whitelist']:
            return True

        for option in filters['root_whitelist']:
            filter_passed = True
            # check if attributes are valid
            for key in option.keys():
                if key not in ROOT_WHITELIST_OPTIONS:
                    # key not in feats and not negated
                    if key not in feats:
                        if not option[key][0]:
                            filter_passed = False
                    # key different, then in head and not negated
                    elif option[key][1] != feats[key] and not option[key][0]:
                        filter_passed = False
                    # key equal, and negated
                    elif option[key][1] == feats[key] and option[key][0]:
                        filter_passed = False

            filter_passed = filter_passed and \
                ('deprel' not in option or (option['deprel'][1] == deprel) == (not option['deprel'][0])) and \
                ('form' not in option or (option['form'][1] == form) == (not option['form'][0])) and \
                ('lemma' not in option or (option['lemma'][1] == lemma) == (not option['lemma'][0])) and \
                ('upos' not in option or (option['upos'][1] == upos) == (not option['upos'][0])) and \
                ('misc' not in option or (option['misc'][1] == misc) == (not option['misc'][0]))

            if filter_passed:
                return True

        return False

    @staticmethod
    def check_label_whitelist(deprel, filters):
        """
        When label whitelist exists, check if deprel is in it.
        :param deprel:
        :param filters:
        :return:
        """
        return not filters['label_whitelist'] or deprel in filters['label_whitelist']
