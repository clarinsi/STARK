
class Result(object):
    def __init__(self, string, order):
        self.key = string
        self.key_split = [string]
        # order with original numbers in sentences
        self.build_order = [order]
        # order with numbers from 0 to n of n-gram
        self.final_order = ''
