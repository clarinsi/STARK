import copy


class Result(object):
    def __init__(self, string, architecture_order):
        self.key = string
        self.order_key = str([architecture_order])
        self.array = [string]
        # order with original numbers in sentences
        # self.order = str([architecture_order])
        # order with numbers from 0 to n of n-gram
        self.final_order = ''
        self.separators = []

    def __repr__(self):
        return self.key

    def add(self, string, architecture_order, separator, is_left):
        if is_left:
            self.array = [string] + self.array
            # self.order = [architecture_order] + self.order
            self.separators = [separator] + self.separators
            self.key = string + ' ' + separator + ' ' + self.key
            self.order_key = architecture_order + ' ' + separator + ' ' + self.order_key

        else:
            self.array += [string]
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

    def merge_results(self, right_t, separator, left=True):
        left_tree = copy.copy(self)
        right_tree = copy.copy(right_t)

        if separator:
            if left:
                # merged_results.append(left_part + right_part + separator)
                left_tree.key = left_tree.key + right_tree.key + separator
                left_tree.order_key = left_tree.order_key + right_tree.order_key + separator
                left_tree.array = left_tree.array + right_tree.array
                # left_tree.order = str([architecture_order])
                left_tree.separators = left_tree.separators + right_tree.separators + [separator]
            else:
                # merged_results.append(left_part + separator + right_part)
                left_tree.key = left_tree.key + separator + right_tree.key
                left_tree.order_key = left_tree.order_key + separator + right_tree.order_key
                left_tree.array = left_tree.array + right_tree.array
                # left_tree.order = str([architecture_order])
                left_tree.separators = left_tree.separators + [separator] + right_tree.separators
        else:
            # merged_results.append(left_part + right_part)
            left_tree.key = left_tree.key + right_tree.key
            left_tree.order_key = left_tree.order_key + right_tree.order_key
            left_tree.array = left_tree.array + right_tree.array
            # left_tree.order = str([architecture_order])
            left_tree.separators = left_tree.separators + right_tree.separators

        return left_tree

    def put_in_bracelets(self):
        result = copy.copy(self)
        result.key = ('(' + result.key + ')')
        result.order_key = ('(' + result.order_key + ')')
        return result

    def finalize_result(self):
        result = copy.copy(self)
        result.key = result.key[1:-1]
        # result.order_key = result.order_key[1:-1]
        # TODO When tree is finalized create relative word order (alphabet)!
        return result
