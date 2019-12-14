import copy
import string

from generic import create_output_string_form, create_output_string_deprel, create_output_string_lemma, \
    create_output_string_upos, create_output_string_xpos, create_output_string_feats, generate_key


class Result(object):
    def __init__(self, node, architecture_order, create_output_strings):
        # self.array = [[create_output_string(node) for create_output_string in create_output_strings]]
        # if create_output_string_lemma in create_output_strings:
        #     key_array = [[create_output_string(node) if create_output_string != create_output_string_lemma else 'L=' + create_output_string(node) for create_output_string in create_output_strings]]
        # else:
        #     key_array = self.array
        # if len(self.array[0]) > 1:
        #     self.key = '&'.join(key_array[0])
        # else:
        #     # output_string = create_output_strings[0](node)
        #     self.key = key_array[0][0]

        self.array, self.key = generate_key(node, create_output_strings)
        self.key_free = self.key
            # self.array = [[output_string]]
        self.order_key = str(architecture_order)
        self.order = [architecture_order]
        self.deprel = node.deprel.get_value()
        # order with original numbers in sentences
        # self.order = str([architecture_order])
        # order with numbers from 0 to n of n-gram
        self.root = ''
        self.final_order = ''
        self.separators = []

    def __repr__(self):
        return self.key

    def add(self, string, architecture_order, separator, is_left):
        if is_left:
            self.array = [string] + self.array
            self.order = [architecture_order] + self.order
            # self.order = [architecture_order] + self.order
            self.separators = [separator] + self.separators
            self.key = string + ' ' + separator + ' ' + self.key
            self.order_key = architecture_order + ' ' + separator + ' ' + self.order_key

        else:
            self.array += [string]
            self.order += [architecture_order]
            # self.order += [architecture_order]
            self.separators += [separator]

            self.key += ' ' + separator + ' ' + string
            self.order_key += ' ' + separator + ' ' + architecture_order

    def add_separator(self, separator, left=True):
        self_copy = copy.copy(self)
        if left:
            self_copy.separators += [separator]
            self_copy.key += separator
            self_copy.order_key += separator
        else:
            self_copy.separators = [separator] + self_copy.separators
            self_copy.key = separator + self_copy.key
            self_copy.order_key = separator + self_copy.order_key
        return self_copy

    # def merge_results2(self):


    def merge_results(self, right_t, separator, left=True):
        left_tree = copy.copy(self)
        right_tree = copy.copy(right_t)

        if separator:
            if left:
                # merged_results.append(left_part + right_part + separator)
                left_tree.key = left_tree.key + right_tree.key + separator
                left_tree.order_key = left_tree.order_key + right_tree.order_key + separator
                left_tree.array = left_tree.array + right_tree.array
                left_tree.order = left_tree.order + right_tree.order
                # left_tree.order = str([architecture_order])
                left_tree.separators = left_tree.separators + right_tree.separators + [separator]
            else:
                # merged_results.append(left_part + separator + right_part)
                left_tree.key = left_tree.key + separator + right_tree.key
                left_tree.order_key = left_tree.order_key + separator + right_tree.order_key
                left_tree.array = left_tree.array + right_tree.array
                left_tree.order = left_tree.order + right_tree.order
                # left_tree.order = str([architecture_order])
                left_tree.separators = left_tree.separators + [separator] + right_tree.separators
        else:
            # merged_results.append(left_part + right_part)
            left_tree.key = left_tree.key + right_tree.key
            left_tree.order_key = left_tree.order_key + right_tree.order_key
            left_tree.array = left_tree.array + right_tree.array
            left_tree.order = left_tree.order + right_tree.order
            # left_tree.order = str([architecture_order])
            left_tree.separators = left_tree.separators + right_tree.separators

        return left_tree

    def extend_answer(self, other_answer, separator):
        self.array.extend(other_answer.array)
        self.order.extend(other_answer.order)
        self.key += separator + other_answer.key
        self.order_key += separator + other_answer.order_key
        self.separators.extend(separator)

    def put_in_bracelets(self, inplace=False):
        if inplace:
            self.key = ('(' + self.key + ')')
            self.order_key = ('(' + self.order_key + ')')
            return
        result = copy.copy(self)
        result.key = ('(' + result.key + ')')
        result.order_key = ('(' + result.order_key + ')')
        return result

    def finalize_result(self):
        result = copy.copy(self)
        result.key = result.key[1:-1]
        result.set_root()

        # create order letters
        order_letters = [''] * len(result.order)
        for i in range(len(result.order)):
            ind = result.order.index(min(result.order))
            result.order[ind] = 10000
            order_letters[ind] = string.ascii_uppercase[i]
        result.order = ''.join(order_letters)
        # result.order_key = result.order_key[1:-1]
        # TODO When tree is finalized create relative word order (alphabet)!
        return result

    def set_root(self):
        if len(self.array[0]) > 1:
            self.root = '&'.join(self.array[0])
        else:
            # output_string = create_output_strings[0](node)
            self.root = self.array[0][0]