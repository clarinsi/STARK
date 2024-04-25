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

import copy
import string


class ResultTree(object):
    def __init__(self, node, children, filters):
        self.node = node
        self.children = children
        self.filters = filters
        # value of self.key might change in __repr__() when that chunk executes (self.children, self.key and
        # self.node must be defined)
        self.key = None
        self.order_key = None
        self.order = None
        self.order_ids = None
        self.array = None

    def __repr__(self):
        return self.get_key()

    def set_children(self, children):
        self.children = children

    def reset_params(self):
        self.key = None
        self.order_key = None
        self.order = None
        self.array = None

    def get_grew(self):
        nodes = [self.node]
        links = []

        if self.children:
            for child in self.children:
                links.append((self.node, child.node))
                c_nodes, c_links = child.get_grew()
                nodes.extend(c_nodes)
                links.extend(c_links)

        return nodes, links

    def ignore_nodes(self):
        """
        Drops nodes in result tree, that are supposed to be ignored.
        """
        self.children = [child for child in self.children if child.node.deprel not in self.filters['ignore_labels']]
        for child in self.children:
            child.ignore_nodes()

    def get_key(self):
        """
        A code that returns and (if necessary generates) key of a tree. (used for `Tree` column in output)
        :return:
        key: Key of a tree
        """
        if self.key:
            return self.key
        key = ''
        write_self_node_to_result = False
        if self.children:
            children = self.children
            for child in children:
                if self.filters['node_order'] and child.node.location < self.node.location:
                    if self.filters['dependency_type']:
                        separator = ' <' + child.node.deprel + ' '
                    else:
                        separator = ' < '
                    key += child.get_key() + separator
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        key += self.node.name
                    if self.filters['dependency_type']:
                        separator = ' >' + child.node.deprel + ' '
                    else:
                        separator = ' > '
                    key += separator + child.get_key()

            if not write_self_node_to_result:
                key += self.node.name
            self.key = '(' + key + ')'
        else:
            self.key = self.node.name
        return self.key

    def get_key_sorted(self):
        key = ''
        write_self_node_to_result = False
        if self.children:
            children = sorted(self.children, key=lambda x: x.node.name)
            for child in children:
                if not write_self_node_to_result:
                    write_self_node_to_result = True
                    key += self.node.name
                if self.filters['dependency_type']:
                    separator = ' >' + child.node.deprel + ' '
                else:
                    separator = ' > '
                key += separator + child.get_key_sorted()

            if not write_self_node_to_result:
                key += self.node.name
            key = '(' + key + ')'
        else:
            key = self.node.name
        return key

    def get_order_key(self):
        if self.order_key:
            return self.order_key
        order_key = ''
        write_self_node_to_result = False
        if self.children:
            for child in self.children:
                if self.filters['node_order'] and child.node.location < self.node.location:
                    if self.filters['dependency_type']:
                        separator = ' <' + child.node.deprel + ' '
                    else:
                        separator = ' < '
                    order_key += child.get_order_key() + separator
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        order_key += str(self.node.location)
                    if self.filters['dependency_type']:
                        separator = ' >' + child.node.deprel + ' '
                    else:
                        separator = ' > '
                    order_key += separator + child.get_order_key()
            if not write_self_node_to_result:
                order_key += str(self.node.location)
            self.order_key = '(' + order_key + ')'
        else:
            self.order_key = str(self.node.location)
        return self.order_key

    def get_order(self):
        if self.order:
            return self.order
        order = []
        write_self_node_to_result = False
        if self.children:
            for child in self.children:
                if self.filters['node_order'] and child.node.location < self.node.location:
                    order += child.get_order()
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        order += [self.node.location]
                    order += child.get_order()

            if not write_self_node_to_result:
                order += [self.node.location]
            self.order = order
        else:
            self.order = [self.node.location]
        return self.order

    def get_array(self):
        if self.array:
            return self.array
        array = []
        write_self_node_to_result = False
        if self.children:
            for child in self.children:
                if self.filters['node_order'] and child.node.location < self.node.location:
                    array += child.get_array()
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        array += [self.node.name_parts]
                    array += child.get_array()

            if not write_self_node_to_result:
                array += [self.node.name_parts]
            self.array = array
        else:
            self.array = [self.node.name_parts]
        return self.array

    def finalize_result(self):
        result = copy.copy(self)
        result.reset_params()
        if result.filters['ignore_labels']:
            result.ignore_nodes()

        # create order letters
        order = result.get_order()
        result.order_ids = order.copy()
        order_letters = [''] * len(result.order)
        for i in range(len(order)):
            ind = order.index(min(order))
            order[ind] = 10000
            order_letters[ind] = string.ascii_uppercase[i]
        result.order = ''.join(order_letters)
        return result

    def get_location_mapper(self):
        mapper = {}
        location_array = self.get_array_location()
        for i in range(len(location_array)):
            mapper[location_array[i]] = string.ascii_uppercase[i]
            # order_letters[ind] = string.ascii_uppercase[i]
        # result = copy.copy(self)
        # result.reset_params()
        # mapper = {}
        # # create order letters
        # order = result.get_order()
        # order_letters = [''] * len(result.order)
        # for i in range(len(order)):
        #     ind = order.index(min(order))
        #     order_letters[ind] = string.ascii_uppercase[i]
        #     mapper[order[ind]] = string.ascii_uppercase[i]
        #     order[ind] = 10000
        # result.order = ''.join(order_letters)
        return mapper

    def get_array_location(self):
        array = []
        write_self_node_to_result = False
        if self.children:
            for child in self.children:
                if self.filters['node_order'] and child.node.location < self.node.location:
                    array += child.get_array_location()
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        array += [self.node.location]
                    array += child.get_array_location()

            if not write_self_node_to_result:
                array += [self.node.location]
        else:
            array = [self.node.location]
        return array
