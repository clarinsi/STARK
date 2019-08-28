import sys

from pyconll.unit import Token

from Value import Value


class Tree(object):
    def __init__(self, form, lemma, upos, xpos, deprel, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, head):
        # form_unicode = str(form).encode("utf-8")
        if form not in form_dict:
            form_dict[form] = Value(form)
        self.form = form_dict[form]
        if lemma not in lemma_dict:
            lemma_dict[lemma] = Value(lemma)
        self.lemma = lemma_dict[lemma]
        if upos not in upos_dict:
            upos_dict[upos] = Value(upos)
        self.upos = upos_dict[upos]
        if xpos not in xpos_dict:
            xpos_dict[xpos] = Value(xpos)
        self.xpos = xpos_dict[xpos]
        if deprel not in deprel_dict:
            deprel_dict[deprel] = Value(deprel)
        self.deprel = deprel_dict[deprel]
        # self.position = position

        self.parent = head
        self.l_children = []
        self.r_children = []

    def add_l_child(self, child):
        self.l_children.append(child)

    def add_r_child(self, child):
        self.r_children.append(child)

    def set_parent(self, parent):
        self.parent = parent

    def fits_static_requirements(self, query_tree):
        return ('form' not in query_tree or query_tree['form'] == self.form.get_value) and \
               ('lemma' not in query_tree or query_tree['lemma'] == self.lemma.get_value) and \
               ('upos' not in query_tree or query_tree['upos'] == self.upos.get_value) and \
               ('xpos' not in query_tree or query_tree['xpos'] == self.xpos.get_value) and \
               ('deprel' not in query_tree or query_tree['deprel'] == self.deprel.get_value)

    def generate_children_queries(self, all_query_indices):
        subtree_outcomes = []
        # list of pairs (index of query in group, group of query, is permanent)
        child_queries_metadata = []
        for child_index, child in enumerate(self.l_children):
            new_queries = []

            # add continuation queries to children
            for (result_part_index, result_index, is_permanent), subtree_outcome in zip(child_queries_metadata, subtree_outcomes):
                if subtree_outcome:
                    if len(all_query_indices[result_index][0]) > result_part_index + 1:
                        new_queries.append((result_part_index + 1, result_index, is_permanent))
                    # else:
                    #     completed_subtrees.append((child, result_index))

            child_queries_metadata = new_queries

            # add new queries to children
            for result_index, (group, is_permanent) in enumerate(all_query_indices):
                # check if node has enough children for query to be possible
                if len(self.l_children) - len(group) >= child_index:
                    child_queries_metadata.append((0, result_index, is_permanent))

            child_queries = []
            for result_part_index, result_index, _ in child_queries_metadata:
                child_queries.append(all_query_indices[result_index][0][result_part_index])

            subtree_outcomes = yield child, child_queries, child_queries_metadata
        yield None, None, None

    def add_subtrees(self, old_subtree, new_subtree):
        old_subtree.extend(new_subtree)


    def get_results(self, partial_results_dict, result_index, result_part, outcome, last_result_part):
        # save results for later usage

        # if result index already in and element 0 exists (otherwise error)
        if result_index in partial_results_dict and 0 in partial_results_dict[result_index]:
            if result_part - 1 in partial_results_dict[result_index]:
                if result_part in partial_results_dict[result_index]:
                    partial_results_dict[result_index][result_part].extend(self.merge_results(partial_results_dict[result_index][result_part - 1], outcome))
                else:
                    partial_results_dict[result_index][result_part] = self.merge_results(partial_results_dict[result_index][result_part - 1], outcome)

            # extend one word layer with output
            else:
                partial_results_dict[result_index][0].extend(outcome)
        else:
            partial_results_dict[result_index] = {0: outcome}

        if last_result_part - 1 in partial_results_dict[result_index]:
            return partial_results_dict[result_index].pop(last_result_part - 1)
        return []

    def group_results(self, new_partial_subtrees, child_queries_metadata, all_query_indices, completed_subtrees, partial_results_dict, partial_subtrees):
        for outcome, (result_part, result_index, is_permanent) in zip(new_partial_subtrees, child_queries_metadata):
            if outcome:
                new_results = self.get_results(partial_results_dict, result_index, result_part, outcome, len(all_query_indices[result_index][0]))
                if new_results:
                    if is_permanent:
                        # if result_index in completed_subtrees:
                        #     self.add_subtrees(completed_subtrees[result_index], new_results)
                        # else:
                        #     completed_subtrees[result_index] = new_results
                        # comment
                        self.add_subtrees(completed_subtrees[result_index], new_results)
                    else:
                        # if result_index in completed_subtrees:
                        #     self.add_subtrees(partial_subtrees[result_index], new_results)
                        # else:
                        #     partial_subtrees[result_index] = new_results
                        self.add_subtrees(partial_subtrees[result_index - len(completed_subtrees)], new_results)
            else:
                if not is_permanent:
                    partial_subtrees[result_index - len(completed_subtrees)].append([])

    def get_all_query_indices(self, temporary_query_trees_size, completed_subtrees_size, permanent_query_trees, l_all_query_indices):
        partial_subtrees = [[] for i in range(temporary_query_trees_size)]
        completed_subtrees = [[] for i in range(completed_subtrees_size)]

        # list of pairs (index of query in group, group of query)
        partial_results_dict = {}

        children_queries_generator = self.generate_children_queries(l_all_query_indices)

        child_index = 0
        child, child_queries, child_queries_metadata = next(children_queries_generator)
        while child:
            # obtain children results
            new_partial_subtrees, new_completed_subtrees = child.get_subtrees(permanent_query_trees, child_queries)

            self.group_results(new_partial_subtrees, child_queries_metadata, l_all_query_indices, new_completed_subtrees,
                               partial_results_dict, partial_subtrees)
            # TODO: Right children functionality
            for i in range(len(new_completed_subtrees)):
                completed_subtrees[i].extend(new_completed_subtrees[i])
            child, child_queries, child_queries_metadata = children_queries_generator.send(new_partial_subtrees)
            child_index += 1

        return partial_subtrees, completed_subtrees

    def get_subtrees(self, permanent_query_trees, temporary_query_trees):
        """

        :param permanent_query_trees:
        :param temporary_query_trees:
        """

        # list of all children queries grouped by parent queries
        l_all_query_indices = []
        r_all_query_indices = []

        active_permanent_querry_trees = []

        for permanent_query_tree in permanent_query_trees:
            if self.fits_static_requirements(permanent_query_tree):
                active_permanent_querry_trees.append(permanent_query_tree)
                l_all_query_indices.append((permanent_query_tree['l_children'], True))
                r_all_query_indices.append((permanent_query_tree['r_children'], True))

        # active_temporary_query_tree = []

        partial_subtrees = [[] for i in range(len(temporary_query_trees))]

        for i, temporary_query_tree in enumerate(temporary_query_trees):
            if self.fits_static_requirements(temporary_query_tree):
                # active_temporary_query_tree.append(temporary_query_tree)
                if 'l_children' in temporary_query_tree:
                    l_all_query_indices.append((temporary_query_tree['l_children'], False))
                if 'r_children' in temporary_query_tree:
                    r_all_query_indices.append((temporary_query_tree['r_children'], False))
                if 'l_children' not in temporary_query_tree and 'r_children' not in temporary_query_tree:
                    partial_subtrees[i] = [[self.create_output_string()]]
            # elif 'l_children' not in temporary_query_tree and 'r_children' not in temporary_query_tree:
            #     partial_subtrees[i] = None


        l_partial_subtrees, l_completed_subtrees = self.get_all_query_indices(len(temporary_query_trees), len(permanent_query_trees), permanent_query_trees, l_all_query_indices)
        merged_partial_subtrees = []
        for i in range(len(l_partial_subtrees)):
            if l_partial_subtrees[i]:
                merged_partial_subtrees.append(self.merge_results(l_partial_subtrees[i], [[self.create_output_string()]]))
            else:
                merged_partial_subtrees.append(partial_subtrees[i])
        return merged_partial_subtrees, l_completed_subtrees

    @staticmethod
    def merge_results(old_results, new_results):
        merged_results = []
        for old_result in old_results:
            for new_result in new_results:
                merged_results.append(old_result + new_result)
        return merged_results

    def create_output_string(self):
        return self.form.get_value()
