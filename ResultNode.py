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
