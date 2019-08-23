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

    def generate_children_queries(self, l_all_query_indices):
        subtree_outcomes = []
        # list of pairs (index of query in group, group of query)
        queries = []
        for child_index, child in enumerate(self.l_children):
            new_queries = []

            # add continuation queries to children
            for (result_part_index, result_index, is_permanent), subtree_outcome in zip(queries, subtree_outcomes):
                if subtree_outcome:
                    if len(l_all_query_indices[result_index][0]) > result_part_index + 1:
                        new_queries.append((result_part_index + 1, result_index, is_permanent))
                    # else:
                    #     completed_subtrees.append((child, result_index))

            queries = new_queries

            # add new queries to children
            for result_index, (group, is_permanent) in enumerate(l_all_query_indices):
                # check if node has enough children for query to be possible
                if len(self.l_children) - len(group) >= child_index:
                    queries.append((0, result_index, is_permanent))

            l_children_query_trees = []
            for result_part_index, result_index, _ in queries:
                l_children_query_trees.append(l_all_query_indices[result_index][0][result_part_index])

            subtree_outcomes = yield child, l_children_query_trees, queries
        yield None, None, None

    def add_subtrees(self, old_subtree, new_subtree):
        old_subtree.extend(new_subtree)

    def group_results_old(self, subtree_outcomes, queries, l_all_query_indices, completed_subtrees, query_creation_dict, child_index, partial_subtrees):
        for outcome, (result_part_index, result_index, is_permanent) in zip(subtree_outcomes, queries):
            if outcome:
                if result_part_index == len(l_all_query_indices[result_index][0]) - 1:
                    new_results = self.create_subtrees(query_creation_dict, result_index, result_part_index, child_index, outcome)
                    if is_permanent:
                        self.add_subtrees(completed_subtrees, new_results)

                    else:
                        self.add_subtrees(partial_subtrees, new_results)
                else:
                    # save results for later usage
                    if result_index in query_creation_dict:
                        if result_part_index in query_creation_dict[result_index]:
                            query_creation_dict[result_index][result_part_index][child_index] = outcome
                        else:
                            query_creation_dict[result_index][result_part_index] = {child_index: outcome}
                    else:
                        query_creation_dict[result_index] = {result_part_index: {child_index: outcome}}
            else:
                if not is_permanent:
                    partial_subtrees.append(None)


    def add_partial_results(self, partial_results_dict, result_index, result_part_index, child_index, outcome):
        # save results for later usage
        # if result_index in partial_results_dict:
        #     if result_part_index in partial_results_dict[result_index]:
        #         # previous_results, previous_stage = partial_results_dict[result_index][result_part_index]
        #         partial_results_dict[result_index][result_part_index] = self.add_results_part(partial_results_dict[result_index][result_part_index], outcome)
        #     else:
        #         partial_results_dict[result_index][result_part_index] = outcome
        # else:
        #     partial_results_dict[result_index] = {result_part_index: outcome}



        if result_index in partial_results_dict:
            if result_part_index in partial_results_dict[result_index]:
                # previous_results, previous_stage = partial_results_dict[result_index][result_part_index]
                partial_results_dict[result_index][result_part_index] = self.add_results_part(partial_results_dict[result_index][result_part_index], self.create_tuple_from_output(outcome, []))
            else:
                partial_results_dict[result_index][result_part_index] = self.create_tuple_from_output(outcome, [])
        else:
            partial_results_dict[result_index] = {result_part_index: self.create_tuple_from_output(outcome, [])}

    # def create_tuple_from_output(self, new_results, combined_results):
    #     for new_result in new_results:
    #         combined_results.append((new_result, 0))
    #     return combined_results

    def add_results_part(self, previous_results_part, new_results):
        combined_results = self.merge_results(previous_results_part, new_results)

        return self.create_tuple_from_output(new_results, combined_results=combined_results)
        # for new_result in new_results:
        #     combined_results.append((new_result, 0))
        # return combined_results

    def group_results(self, subtree_outcomes, queries, l_all_query_indices, completed_subtrees, partial_results_dict, child_index, partial_subtrees):
        for outcome, (result_part_index, result_index, is_permanent) in zip(subtree_outcomes, queries):
            if outcome:
                if result_part_index == len(l_all_query_indices[result_index][0]) - 1:
                    # new_results = self.create_subtrees(partial_results_dict, result_index, result_part_index, child_index, outcome)
                    if result_part_index > 0:
                        new_results = self.merge_results(partial_results_dict[result_index][result_part_index - 1],
                                                         outcome)
                    else:
                        new_results = outcome

                    if is_permanent:
                        self.add_subtrees(completed_subtrees, new_results)
                    else:
                        self.add_subtrees(partial_subtrees, new_results)
                else:
                    self.add_partial_results(partial_results_dict, result_index, result_part_index, child_index, outcome)
            else:
                if not is_permanent:
                    partial_subtrees.append(None)

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

        active_temporary_query_tree = []
        partial_subtrees = list([None] * len(temporary_query_trees))

        for i, temporary_query_tree in enumerate(temporary_query_trees):
            if self.fits_static_requirements(temporary_query_tree):
                active_temporary_query_tree.append(temporary_query_tree)
                if 'l_children' in temporary_query_tree:
                    l_all_query_indices.append((temporary_query_tree['l_children'], False))
                if 'r_children' in temporary_query_tree:
                    r_all_query_indices.append((temporary_query_tree['r_children'], False))
                if 'l_children' not in temporary_query_tree and 'r_children' not in temporary_query_tree:
                    partial_subtrees[i] = [[self.create_output_string()]]
            elif 'l_children' not in temporary_query_tree and 'r_children' not in temporary_query_tree:
                partial_subtrees[i] = None
            # if self.fits_static_requirements(temporary_query_tree):
            #     if temporary_query_tree['l_children'] and self.l_children:
            #         l_children_permanent_query_trees.append(temporary_query_tree['l_children'])
            #     if temporary_query_tree['r_children'] and self.r_children:
            #         r_children_permanent_query_trees.append(temporary_query_tree['r_children'])



        # tree_outcomes = []
        completed_subtrees = []
        # list of pairs (index of query in group, group of query)
        queries = []
        subtree_outcomes = []
        query_creation_dict = {}


        children_queries_generator = self.generate_children_queries(l_all_query_indices)

        # # children_queries_generator.send([])
        # a = next(children_queries_generator)
        # a1 = children_queries_generator.send(list([True] * len(a)))
        # # b = next(children_queries_generator)
        # b1 = children_queries_generator.send(list([True] * len(a1)))
        # # c = next(children_queries_generator)
        # c1 = children_queries_generator.send(list([True] * len(b1)))
        # # d = next(children_queries_generator)
        # d1 = children_queries_generator.send(list([True] * len(c1)))
        child_index = 0
        child, child_query, child_group_mapper = next(children_queries_generator)
        while child:
            subtree_outcomes, completed_subtrees = child.get_subtrees(permanent_query_trees, child_query)

            self.group_results(subtree_outcomes, child_group_mapper, l_all_query_indices, completed_subtrees, query_creation_dict, child_index, partial_subtrees)
            # TODO
            child, child_query, child_group_mapper = children_queries_generator.send(subtree_outcomes)
            child_index += 1
            print('test')

        # for child_index, child in enumerate(self.l_children):
        #     # add continuation queries to children
        #     for (result_part_index, query_indices_index, is_permanent), subtree_outcome in zip(queries, subtree_outcomes):
        #         if subtree_outcome:
        #             if len(l_all_query_indices[query_indices_index]) > result_part_index + 1:
        #                 queries.append((result_part_index + 1, query_indices_index, is_permanent))
        #             # else:
        #             #     completed_subtrees.append((child, query_indices_index))
        #
        #     # add new queries to children
        #     for query_indices_index, (query_indices, is_permanent) in enumerate(l_all_query_indices):
        #         # check if node has enough children for query to be possible
        #         if len(self.l_children) - len(query_indices) >= child_index:
        #             queries.append((0, query_indices_index, is_permanent))
        #
        #
        #     l_children_query_trees = []
        #     for result_part_index, query_indices_index, _ in queries:
        #         l_children_query_trees.append(l_all_query_indices[query_indices_index][0][result_part_index])
        #     subtree_outcomes, completed_subtrees = child.get_subtrees(permanent_query_trees, l_children_query_trees)
        #
        #
        #
        #     # TODO: Right children functionality
        #
        #
        #
        #     for outcome, (result_part_index, query_indices_index, is_permanent) in zip(subtree_outcomes, queries):
        #         if outcome:
        #             if result_part_index == len(l_all_query_indices[query_indices_index]) - 1:
        #                 if is_permanent:
        #                     completed_subtrees.extend(self.create_output(temp_results, query_indices_index, result_part_index, child_index))
        #                 else:
        #                     partial_subtrees.append(self.create_output(temp_results, query_indices_index, result_part_index, child_index))
        #             else:
        #                 # save results for later usage
        #                 if child_index in temp_results:
        #                     if query_indices_index in temp_results[child_index]:
        #                         temp_results[child_index][query_indices_index][result_part_index] = outcome
        #                     else:
        #                         temp_results[child_index][query_indices_index] = {result_part_index: outcome}
        #                 else:
        #                     temp_results[child_index] = {query_indices_index: {result_part_index: outcome}}
        #         else:
        #             if not is_permanent:
        #                 partial_subtrees.append(None)
        return partial_subtrees, completed_subtrees

    @staticmethod
    def merge_results(old_results, new_results):
        # previous_results, previous_stage = partial_results_dict[result_index][result_part_index]
        merged_results = []
        # old_results, old_stage = old_results_tuple
        for old_result, old_stage in old_results:
            for new_result in new_results:
                merged_results.append((old_result + new_result, old_stage + 1))
        # if not old_results:
        #     return new_results
        return merged_results

    def create_subtrees(self, query_creation_dict, result_index, result_part_index, child_index, outcome):
        new_valid_subtrees = []
        # stores all result_parts that have specific child_index together
        result_connections = {}
        for i in range(result_part_index):
            for j in range(child_index):
                # if child indices exist in result_index and result_part_index plus index of part is higher or equal to index of child (otherwise it is not in query_creation_dict
                if result_index in query_creation_dict and i in query_creation_dict[result_index] and j in query_creation_dict[result_index][i]:
                # if result_index in query_creation_dict and i in query_creation_dict[result_index] and j in query_creation_dict[result_index][i] and i >= j:
                    if i in result_connections:
                        result_connections[i].append(j)
                    else:
                        result_connections[i] = [j]
                    # positioned_candidates[j] = (query_creation_dict[i][result_index][j])

        # result = []
        return self.create_subtrees_from_result_connections(0, 0, result_part_index, query_creation_dict, result_connections, result_index, [], outcome)
        # new_valid_subtrees.extend(outcome[])
        # outcome.append(self.create_output_string())

    def create_subtrees_from_result_connections(self, child_index_i, result_part_index_i, result_part_index_final, query_creation_dict, result_connections,
                                                 result_index, res_array, outcome):
        if result_part_index_i == result_part_index_final:
            # self.merge_results(res_array, outcome)
            return self.merge_results(res_array, outcome)



        # res_array.append(query_creation_dict[result_index][result_part_index_i][child_index_i])
        results = []

        for child_index in result_connections[result_part_index_i]:
            if not (result_index in query_creation_dict and result_part_index_i in query_creation_dict[
                result_index] and child_index_i in query_creation_dict[result_index][result_part_index_i]):
                print('HERE!')
                return []

            pass_array = self.merge_results(res_array,
                                            query_creation_dict[result_index][result_part_index_i][child_index])
            # if child_index >= result_part_index_i:
            results.extend(self.create_subtrees_from_result_connections(child_index, result_part_index_i + 1, result_part_index_final, query_creation_dict,
                                                                        result_connections, result_index, res_array, outcome))

        # print('aaa')
        return results

    def create_output_string(self):
        return self.form.get_value()