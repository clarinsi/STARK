import copy
import string

from generic import create_output_string_form, create_output_string_deprel, create_output_string_lemma, \
    create_output_string_upos, create_output_string_xpos, create_output_string_feats, generate_key


class ResultTree(object):
    def __init__(self, node, children, filters):
        self.node = node
        self.children = children
        self.filters = filters
        self.key = None
        self.order_key = None
        self.order = None
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

    def get_key(self):
        if self.key:
            return self.key
        key = ''
        write_self_node_to_result = False
        if self.children:
            children = self.children
            for child in children:
                if self.filters['node_order'] and child.node.location < self.node.location:
                    if self.filters['dependency_type']:
                        # separator = ' <' + deprel[i_child][i_answer] + ' '
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
                        # separator = ' <' + deprel[i_child][i_answer] + ' '
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

    # def add(self, string, architecture_order, separator, is_left):
    #     if is_left:
    #         self.array = [string] + self.array
    #         self.order = [architecture_order] + self.order
    #         # self.order = [architecture_order] + self.order
    #         self.separators = [separator] + self.separators
    #         self.key = string + ' ' + separator + ' ' + self.key
    #         self.order_key = architecture_order + ' ' + separator + ' ' + self.order_key
    #
    #     else:
    #         self.array += [string]
    #         self.order += [architecture_order]
    #         # self.order += [architecture_order]
    #         self.separators += [separator]
    #
    #         self.key += ' ' + separator + ' ' + string
    #         self.order_key += ' ' + separator + ' ' + architecture_order

    # def add_separator(self, separator, left=True):
    #     self_copy = copy.copy(self)
    #     if left:
    #         self_copy.separators += [separator]
    #         self_copy.key += separator
    #         self_copy.order_key += separator
    #     else:
    #         self_copy.separators = [separator] + self_copy.separators
    #         self_copy.key = separator + self_copy.key
    #         self_copy.order_key = separator + self_copy.order_key
    #     return self_copy

    # def merge_results2(self):


    # def merge_results(self, right_t, separator, left=True):
    #     left_tree = copy.copy(self)
    #     right_tree = copy.copy(right_t)
    #
    #     if separator:
    #         if left:
    #             # merged_results.append(left_part + right_part + separator)
    #             left_tree.key = left_tree.key + right_tree.key + separator
    #             left_tree.order_key = left_tree.order_key + right_tree.order_key + separator
    #             left_tree.array = left_tree.array + right_tree.array
    #             left_tree.order = left_tree.order + right_tree.order
    #             # left_tree.order = str([architecture_order])
    #             left_tree.separators = left_tree.separators + right_tree.separators + [separator]
    #         else:
    #             # merged_results.append(left_part + separator + right_part)
    #             left_tree.key = left_tree.key + separator + right_tree.key
    #             left_tree.order_key = left_tree.order_key + separator + right_tree.order_key
    #             left_tree.array = left_tree.array + right_tree.array
    #             left_tree.order = left_tree.order + right_tree.order
    #             # left_tree.order = str([architecture_order])
    #             left_tree.separators = left_tree.separators + [separator] + right_tree.separators
    #     else:
    #         # merged_results.append(left_part + right_part)
    #         left_tree.key = left_tree.key + right_tree.key
    #         left_tree.order_key = left_tree.order_key + right_tree.order_key
    #         left_tree.array = left_tree.array + right_tree.array
    #         left_tree.order = left_tree.order + right_tree.order
    #         # left_tree.order = str([architecture_order])
    #         left_tree.separators = left_tree.separators + right_tree.separators
    #
    #     return left_tree

    # def extend_answer(self, other_answer, separator):
    #     self.array.extend(other_answer.array)
    #     self.order.extend(other_answer.order)
    #     self.key += separator + other_answer.key
    #     self.order_key += separator + other_answer.order_key
    #     self.separators.extend(separator)

    # def put_in_bracelets(self, inplace=False):
    #     if inplace:
    #         self.key = ('(' + self.key + ')')
    #         self.order_key = ('(' + self.order_key + ')')
    #         return
    #     result = copy.copy(self)
    #     result.key = ('(' + result.key + ')')
    #     result.order_key = ('(' + result.order_key + ')')
    #     return result

    def finalize_result(self):
        result = copy.copy(self)
        result.reset_params()
        # result.key = result.get_key()
        # result.set_root()

        # create order letters
        order = result.get_order()
        order_letters = [''] * len(result.order)
        for i in range(len(order)):
            ind = order.index(min(order))
            order[ind] = 10000
            order_letters[ind] = string.ascii_uppercase[i]
        result.order = ''.join(order_letters)
        # result.order_key = result.order_key[1:-1]
        # TODO When tree is finalized create relative word order (alphabet)!
        return result

    # def set_root(self):
    #     if len(self.array[0]) > 1:
    #         self.root = '&'.join(self.array[0])
    #     else:
    #         # output_string = create_output_strings[0](node)
    #         self.root = self.array[0][0]