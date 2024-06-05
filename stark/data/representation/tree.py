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
import abc
import string


class RepresentationTree(object):
    def __init__(self, node, children):
        self.node = node
        self.children = children

    @classmethod
    @abc.abstractmethod
    def copy(cls, node, children, filters):
        return

    def set_children(self, children):
        self.children = children

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

    def ignore_nodes(self, filters):
        """
        Drops nodes in result tree, that are supposed to be ignored.
        """
        children = [child for child in self.children if child.node.node.deprel not in filters['ignored_labels']]

        new_children = []
        for child in children:
            new_children.append(child.ignore_nodes(filters))

        return self.copy(self.node, new_children, filters)

    def get_key_array(self, filters):
        """
        A code that generates key and array of a tree simultaneously (for faster execution).
        :return:
        key: Key of a tree
        array: Array of tree elements
        """

        array = []
        key = ''
        write_self_node_to_result = False
        if self.children:
            children = self.children
            for child in children:
                if filters['node_order'] and child.node.location < self.node.location:
                    k, a = child.get_key_array(filters)
                    array += a

                    if filters['dependency_type']:
                        separator = ' <' + child.node.node.deprel + ' '
                    else:
                        separator = ' < '
                    key += k + separator
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        key += self.node.name
                        array += [self.node.name_parts]
                    if filters['dependency_type']:
                        separator = ' >' + child.node.node.deprel + ' '
                    else:
                        separator = ' > '
                    k, a = child.get_key_array(filters)
                    array += a
                    key += separator + k

            if not write_self_node_to_result:
                key += self.node.name
                array += [self.node.name_parts]
            array = array
            key = '(' + key + ')'
        else:
            array = [self.node.name_parts]
            key = self.node.name
        return key, array

    def get_key(self, filters):
        """
        A code that returns and (if necessary generates) key of a tree. (used for `Tree` column in output)
        :return:
        key: Key of a tree
        """
        key = ''
        write_self_node_to_result = False
        if self.children:
            children = self.children
            for child in children:
                if filters['node_order'] and child.node.location < self.node.location:
                    if filters['dependency_type']:
                        separator = ' <' + child.node.node.deprel + ' '
                    else:
                        separator = ' < '
                    key += child.get_key(filters) + separator
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        key += self.node.name
                    if filters['dependency_type']:
                        separator = ' >' + child.node.node.deprel + ' '
                    else:
                        separator = ' > '
                    key += separator + child.get_key(filters)

            if not write_self_node_to_result:
                key += self.node.name
            key = '(' + key + ')'
        else:
            key = self.node.name
        return key

    def get_key_sorted(self, filters):
        key = ''
        write_self_node_to_result = False
        if self.children:
            children = sorted(self.children, key=lambda x: x.node.name)
            for child in children:
                if not write_self_node_to_result:
                    write_self_node_to_result = True
                    key += self.node.name
                if filters['dependency_type']:
                    separator = ' >' + child.node.node.deprel + ' '
                else:
                    separator = ' > '
                key += separator + child.get_key_sorted(filters)

            if not write_self_node_to_result:
                key += self.node.name
            key = '(' + key + ')'
        else:
            key = self.node.name
        return key

    def get_order_key(self, filters):
        order_key = ''
        write_self_node_to_result = False
        if self.children:
            for child in self.children:
                if filters['node_order'] and child.node.location < self.node.location:
                    if filters['dependency_type']:
                        separator = ' <' + child.node.node.deprel + ' '
                    else:
                        separator = ' < '
                    order_key += child.get_order_key(filters) + separator
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        order_key += str(self.node.location)
                    if filters['dependency_type']:
                        separator = ' >' + child.node.node.deprel + ' '
                    else:
                        separator = ' > '
                    order_key += separator + child.get_order_key(filters)
            if not write_self_node_to_result:
                order_key += str(self.node.location)
            order_key = '(' + order_key + ')'
        else:
            order_key = str(self.node.location)
        return order_key

    def get_order(self, filters):
        order = []
        write_self_node_to_result = False
        if self.children:
            for child in self.children:
                if filters['node_order'] and child.node.location < self.node.location:
                    order += child.get_order(filters)
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        order += [self.node.location]
                    order += child.get_order(filters)

            if not write_self_node_to_result:
                order += [self.node.location]
            order = order
        else:
            order = [self.node.location]
        return order

    def get_array(self, filters):
        array = []
        write_self_node_to_result = False
        if self.children:
            for child in self.children:
                if filters['node_order'] and child.node.location < self.node.location:
                    array += child.get_array(filters)
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        array += [self.node.name_parts]
                    array += child.get_array(filters)

            if not write_self_node_to_result:
                array += [self.node.name_parts]
            array = array
        else:
            array = [self.node.name_parts]
        return array

    @staticmethod
    def get_order_letters(order):
        order_letters = [''] * len(order)
        for i in range(len(order)):
            ind = order.index(min(order))
            order[ind] = 10000
            order_letters[ind] = string.ascii_uppercase[i % 26]
        return ''.join(order_letters)

    def ignore_labels(self, filters):
        if filters['ignored_labels']:
            return self.ignore_nodes(filters)
        return self

    def get_location_mapper(self, filters):
        mapper = {}
        location_array = self.get_array_location(filters)
        for i in range(len(location_array)):
            mapper[location_array[i]] = string.ascii_uppercase[i] if i < 26 else (string.ascii_uppercase[i % 26] +
                                                                                  str(int(i / 26)))

        return mapper

    def get_array_location(self, filters):
        array = []
        write_self_node_to_result = False
        if self.children:
            for child in self.children:
                if filters['node_order'] and child.node.location < self.node.location:
                    array += child.get_array_location(filters)
                else:
                    if not write_self_node_to_result:
                        write_self_node_to_result = True
                        array += [self.node.location]
                    array += child.get_array_location(filters)

            if not write_self_node_to_result:
                array += [self.node.location]
        else:
            array = [self.node.location]
        return array
