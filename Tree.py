import sys
from copy import copy

from pyconll.unit import Token

from Value import Value


class Tree(object):
    def __init__(self, form, lemma, upos, xpos, deprel, feats, form_dict, lemma_dict, upos_dict, xpos_dict, deprel_dict, feats_dict, feats_complete_dict, head):
        # if not hasattr(self, 'feats'):
        #     self.feats = {}

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
        if feats not in feats_complete_dict:
            feats_complete_dict[feats] = Value(feats)
        self.feats_complete = feats_complete_dict[feats]
        # for feat in feats.keys():
        #     if next(iter(feats[feat])) not in feats_dict[feat]:
        #         feats_dict[feat][next(iter(feats[feat]))] = Value(next(iter(feats[feat])))
        #     if not feat in self.feats:
        #         self.feats[feat] = {}
        #     self.feats[feat][next(iter(feats[feat]))] = feats_dict[feat][next(iter(feats[feat]))]
        # self.position = position

        self.parent = head
        self.children = []
        self.children_split = -1

        self.index = 0

    def add_child(self, child):
        child.index = len(self.children)
        self.children.append(child)

    def set_parent(self, parent):
        self.parent = parent

    # def fits_static_requirements_feats(self, query_tree):
    #     if 'feats' not in query_tree:
    #         return True
    #
    #     for feat in query_tree['feats'].keys():
    #         if feat not in self.feats or query_tree['feats'][feat] != next(iter(self.feats[feat].values())).get_value():
    #             return False
    #
    #     return True


    def fits_static_requirements(self, query_tree):
        return ('form' not in query_tree or query_tree['form'] == self.form.get_value()) and \
               ('lemma' not in query_tree or query_tree['lemma'] == self.lemma.get_value()) and \
               ('upos' not in query_tree or query_tree['upos'] == self.upos.get_value()) and \
               ('xpos' not in query_tree or query_tree['xpos'] == self.xpos.get_value()) and \
               ('deprel' not in query_tree or query_tree['deprel'] == self.deprel.get_value()) and \
               ('feats' not in query_tree or query_tree['feats'] == self.feats_complete.get_value())
               # self.fits_static_requirements_feats(query_tree)

    def generate_children_queries(self, all_query_indices, children):
        partial_results = {}
        # list of pairs (index of query in group, group of query, is permanent)
        child_queries_metadata = []
        for child_index, child in enumerate(children):
            new_queries = []

            # add continuation queries to children
            for result_part_index, result_index, is_permanent in child_queries_metadata:
                if result_index in partial_results and result_part_index in partial_results[result_index] and len(partial_results[result_index][result_part_index]) > 0:
                    if len(all_query_indices[result_index][0]) > result_part_index + 1:
                        new_queries.append((result_part_index + 1, result_index, is_permanent))
                    # else:
                    #     completed_subtrees.append((child, result_index))

            child_queries_metadata = new_queries

            # add new queries to children
            for result_index, (group, is_permanent) in enumerate(all_query_indices):
                # check if node has enough children for query to be possible
                if len(children) - len(group) >= child_index:
                    child_queries_metadata.append((0, result_index, is_permanent))

            child_queries = []
            for result_part_index, result_index, _ in child_queries_metadata:
                child_queries.append(all_query_indices[result_index][0][result_part_index])

            partial_results = yield child, child_queries, child_queries_metadata
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

    def group_results(self, new_partial_subtrees, child_queries_metadata, all_query_indices, partial_results_dict, partial_subtrees):
        for outcome, (result_part, result_index, is_permanent) in zip(new_partial_subtrees, child_queries_metadata):
            if outcome:
                new_results = self.get_results(partial_results_dict, result_index, result_part, outcome, len(all_query_indices[result_index][0]))
                if new_results:
                    self.add_subtrees(partial_subtrees[result_index], new_results)
            else:
                if not is_permanent:
                    partial_subtrees[result_index].append([])

    def get_all_query_indices_old(self, temporary_query_trees_size, completed_subtrees_size, permanent_query_trees, l_all_query_indices, children, create_output_string):
        partial_subtrees = [[] for i in range(completed_subtrees_size + temporary_query_trees_size)]
        completed_subtrees = [[] for i in range(completed_subtrees_size)]

        # list of pairs (index of query in group, group of query)
        partial_results_dict = {}

        children_queries_generator = self.generate_children_queries(l_all_query_indices, children)

        child_index = 0
        child, child_queries, child_queries_metadata = next(children_queries_generator)
        while child:
            # obtain children results
            new_partial_subtrees, new_completed_subtrees = child.get_subtrees(permanent_query_trees, child_queries, create_output_string)

            self.group_results(new_partial_subtrees, child_queries_metadata, l_all_query_indices,
                               partial_results_dict, partial_subtrees)

            for i in range(len(new_completed_subtrees)):
                completed_subtrees[i].extend(new_completed_subtrees[i])
            child, child_queries, child_queries_metadata = children_queries_generator.send(partial_results_dict)
            child_index += 1

        return partial_subtrees, completed_subtrees

    def get_all_query_indices(self, temporary_query_trees_size, completed_subtrees_size, permanent_query_trees, all_query_indices, children, create_output_string, filters):
        # l_partial_subtrees, l_completed_subtrees = self.get_all_query_indices(len(temporary_query_trees),
        #                                                                       len(permanent_query_trees),
        #                                                                       permanent_query_trees,
        #                                                                       l_all_query_indices, self.l_children,
        #                                                                       create_output_string)
        partial_subtrees = [[] for i in range(completed_subtrees_size + temporary_query_trees_size)]
        partial_subtrees_architectures = [[] for i in range(completed_subtrees_size + temporary_query_trees_size)]
        partial_subtrees_index = [[] for i in range(completed_subtrees_size + temporary_query_trees_size)]
        completed_subtrees = [[] for i in range(completed_subtrees_size)]

        # list of pairs (index of query in group, group of query)
        partial_results_dict = {}

        # TODO try to erase!!!
        child_queries = [all_query_indice[0] for all_query_indice in all_query_indices]

        answers_lengths = [len(query) for query in child_queries]

        child_queries_flatten = [query_part for query in child_queries for query_part in query]

        all_new_partial_answers = [[] for query_part in child_queries_flatten]
        all_new_partial_answers_architecture = [[] for query_part in child_queries_flatten]

        # ask children all queries/partial queries
        for child in children:
            # obtain children results
            new_partial_answers_architecture, new_partial_answers, new_completed_subtrees = child.get_subtrees(permanent_query_trees, child_queries_flatten,
                                                                              create_output_string, filters)

            assert len(new_partial_answers) == len(child_queries_flatten)
            for i, new_partial_subtree in enumerate(new_partial_answers):
                all_new_partial_answers[i].append(new_partial_subtree)
                all_new_partial_answers_architecture[i].append(new_partial_answers_architecture[i])

            # add 6 queries from 3 split up
            # self.group_results(new_partial_subtrees, child_queries_metadata, all_query_indices,
            #                    partial_results_dict, partial_subtrees)

            for i in range(len(new_completed_subtrees)):
                completed_subtrees[i].extend(new_completed_subtrees[i])

        # merge answers in appropriate way
        i = 0
        # iterate over all answers per queries
        for answer_i, answer_length in enumerate(answers_lengths):
            # iterate over answers of query
            partial_subtrees[answer_i], partial_subtrees_architectures[answer_i], partial_subtrees_index[answer_i] = self.create_answers(all_new_partial_answers[i:i + answer_length], all_new_partial_answers_architecture[i:i + answer_length], answer_length, filters)
            # while i < answers_length:
            #     self.create_grouped_answers()
            #     i += 1
            i += answer_length

            # merged_results = []
            # for old_result in old_results:
            #     for new_result in new_results:
            #         merged_results.append(old_result + new_result)
            # return merged_results
        # children_queries_generator = self.generate_children_queries(all_query_indices, children)
        #
        # child_index = 0
        # child, child_queries, child_queries_metadata = next(children_queries_generator)
        # while child:
        #     # obtain children results
        #     new_partial_subtrees, new_completed_subtrees = child.get_subtrees(permanent_query_trees, child_queries, create_output_string)
        #
        #     self.group_results(new_partial_subtrees, child_queries_metadata, all_query_indices,
        #                        partial_results_dict, partial_subtrees)
        #
        #     for i in range(len(new_completed_subtrees)):
        #         completed_subtrees[i].extend(new_completed_subtrees[i])
        #     child, child_queries, child_queries_metadata = children_queries_generator.send(partial_results_dict)
        #     child_index += 1

        return partial_subtrees_architectures, partial_subtrees, partial_subtrees_index, completed_subtrees

    def order_dependent_queries(self, active_permanent_query_trees, active_temporary_query_trees, partial_subtrees, partial_subtrees_architecture, partial_subtrees_index,
                                create_output_string, merged_partial_subtrees, merged_partial_subtrees_architecture, i, filters):
        # string_output = ''
        if i < len(active_permanent_query_trees):
            if 'children' in active_permanent_query_trees[i]:
                # if not filters['node_order'] or i_child < self.children_split:
                merged_partial_subtrees.append(
                    self.create_output_children(partial_subtrees[i], [create_output_string(self)], filters, partial_subtrees_index[i]))
                merged_partial_subtrees_architecture.append(
                    self.create_output_children(partial_subtrees_architecture[i], [str([self.index])], filters, partial_subtrees_index[i]))

                # i_child += 1
            else:
                merged_partial_subtrees.append([create_output_string(self)])
                merged_partial_subtrees_architecture.append([str([self.index])])
                # merged_partial_subtrees.append([[create_output_string(self)]])
        else:
            if 'children' in active_temporary_query_trees[i - len(active_permanent_query_trees)]:
                # if not filters['node_order'] or i_child < self.children_split:
                merged_partial_subtrees.append(
                    self.create_output_children(partial_subtrees[i], [create_output_string(self)], filters, partial_subtrees_index[i]))
                merged_partial_subtrees_architecture.append(
                    self.create_output_children(partial_subtrees_architecture[i], [str([self.index])], filters, partial_subtrees_index[i]))

                # i_child += 1
            else:
                merged_partial_subtrees.append([create_output_string(self)])
                merged_partial_subtrees_architecture.append([str([self.index])])
                # merged_partial_subtrees.append([[create_output_string(self)]])

        # return i_child

    def get_subtrees(self, permanent_query_trees, temporary_query_trees, create_output_string, filters):
        """

        :param permanent_query_trees:
        :param temporary_query_trees:
        """

        # list of all children queries grouped by parent queries
        all_query_indices = []

        active_permanent_query_trees = []
        for permanent_query_tree in permanent_query_trees:
            if self.fits_static_requirements(permanent_query_tree):
                active_permanent_query_trees.append(permanent_query_tree)
                if 'children' in permanent_query_tree:
                    all_query_indices.append((permanent_query_tree['children'], True))
                    # r_all_query_indices.append((permanent_query_tree['r_children'], True))

        active_temporary_query_trees = []
        successful_temporary_queries = []
        for i, temporary_query_tree in enumerate(temporary_query_trees):
            if self.fits_static_requirements(temporary_query_tree):
                active_temporary_query_trees.append(temporary_query_tree)
                successful_temporary_queries.append(i)
                # if 'l_children' in temporary_query_tree and 'r_children' in temporary_query_tree:
                if 'children' in temporary_query_tree:
                    all_query_indices.append((temporary_query_tree['children'], False))

        partial_subtrees_architecture, partial_subtrees, partial_subtrees_index, completed_subtrees = self.get_all_query_indices(len(temporary_query_trees),
                                                                                                      len(permanent_query_trees),
                                                                                                      permanent_query_trees,
                                                                                                      all_query_indices, self.children,
                                                                                                      create_output_string, filters)

        merged_partial_subtrees = []
        merged_partial_subtrees_architecture = []
        i = 0
        i_child = 0
        # go over all permanent and temporary query trees
        while i < len(active_permanent_query_trees) + len(active_temporary_query_trees):
            # permanent query trees always have left and right child
            self.order_dependent_queries(active_permanent_query_trees, active_temporary_query_trees, partial_subtrees, partial_subtrees_architecture, partial_subtrees_index,
                                                           create_output_string, merged_partial_subtrees, merged_partial_subtrees_architecture, i, filters)
            # if i < len(active_permanent_query_trees):
            #     if ('l_children' in active_permanent_query_trees[i] and 'r_children' in active_permanent_query_trees[i]):
            #         merged_partial_subtree = self.merge_results(l_partial_subtrees[i_left],
            #                                                     [[create_output_string(self)]])
            #         merged_partial_subtrees.append(
            #             self.merge_results(merged_partial_subtree, r_partial_subtrees[i_right]))
            #         # merged_partial_subtrees.append(self.merge_results(l_partial_subtrees[i], [[create_output_string(self)]]))
            #         i_left += 1
            #         i_right += 1
            #
            #     elif 'l_children' in active_permanent_query_trees[i]:
            #         merged_partial_subtrees.append(
            #             self.merge_results(l_partial_subtrees[i_left], [[create_output_string(self)]]))
            #         i_left += 1
            #
            #     elif 'r_children' in active_permanent_query_trees[i]:
            #         merged_partial_subtrees.append(
            #             self.merge_results([[create_output_string(self)]], r_partial_subtrees[i_right]))
            #         i_right += 1
            #     else:
            #         merged_partial_subtrees.append([[create_output_string(self)]])
            # else:
            #     if ('l_children' in active_temporary_query_trees[i - len(active_permanent_query_trees)] and 'r_children' in active_temporary_query_trees[i - len(active_permanent_query_trees)]):
            #         merged_partial_subtree = self.merge_results(l_partial_subtrees[i_left], [[create_output_string(self)]])
            #         merged_partial_subtrees.append(self.merge_results(merged_partial_subtree, r_partial_subtrees[i_right]))
            #         # merged_partial_subtrees.append(self.merge_results(l_partial_subtrees[i], [[create_output_string(self)]]))
            #         i_left += 1
            #         i_right += 1
            #
            #     elif 'l_children' in active_temporary_query_trees[i - len(active_permanent_query_trees)]:
            #         merged_partial_subtrees.append(self.merge_results(l_partial_subtrees[i_left], [[create_output_string(self)]]))
            #         i_left += 1
            #
            #     elif 'r_children' in active_temporary_query_trees[i - len(active_permanent_query_trees)]:
            #         merged_partial_subtrees.append(self.merge_results([[create_output_string(self)]], r_partial_subtrees[i_right]))
            #         i_right += 1
            #     else:
            #         merged_partial_subtrees.append([[create_output_string(self)]])
            # # if r_partial_subtrees[i]:
            # #     merged_partial_subtrees.append(self.merge_results(l_partial_subtrees[i], [[create_output_string(self)]]))
            i += 1

        # for i in range(len(permanent_query_trees)):
        # for i in range(max(len(completed_subtrees), len(r_completed_subtrees), len(active_permanent_query_trees))):
        for i in range(len(active_permanent_query_trees)):
            # erase first and last braclets when adding new query result
            add_subtree = [subtree[1:-1] for subtree in merged_partial_subtrees[i]]
            # if 0 < len(active_permanent_query_trees):
            completed_subtrees[i].extend(add_subtree)
            # completed_subtrees[i].extend(merged_partial_subtrees[i])

        # answers to valid queries
        subtrees_architecture = [[] for i in range(len(temporary_query_trees))]
        for inside_i, outside_i in enumerate(successful_temporary_queries):
            subtrees_architecture[outside_i] = merged_partial_subtrees_architecture[len(active_permanent_query_trees) + inside_i]

        # answers to valid queries
        subtrees = [[] for i in range(len(temporary_query_trees))]
        for inside_i, outside_i in enumerate(successful_temporary_queries):
            subtrees[outside_i] = merged_partial_subtrees[
                len(active_permanent_query_trees) + inside_i]
        return subtrees_architecture, subtrees, completed_subtrees
        # return merged_partial_subtrees_architecture[len(active_permanent_query_trees):], merged_partial_subtrees[len(active_permanent_query_trees):], completed_subtrees

    @staticmethod
    def merge_results(old_results, new_results):
        merged_results = []
        for old_result in old_results:
            for new_result in new_results:
                merged_results.append(old_result + new_result)
        return merged_results

    @staticmethod
    def merge_answer(answer1, answer2, base_answer_i, answer_j):
        merged_results = []
        merged_indices = []
        for answer1p_i, old_result in enumerate(answer1):
            for answer2p_i, new_result in enumerate(answer2):
                if answer1p_i != answer2p_i:
                    new_indices = [answer1p_i] + [answer2p_i]
                    sorted_indices = sorted(new_indices)

                    if sorted_indices in merged_indices:
                        test = merged_indices.index(sorted(new_indices))
                        # TODO add comparison answers with different indices if equal than ignore
                    merged_results.append(old_result + new_result)
                    merged_indices.append(new_indices)
        return merged_results, merged_indices


    def create_output_children(self, children, new_results, filters, indices):
        merged_results = []
        for i_child, child in enumerate(children):
            for i_new_result, new_result in enumerate(new_results):
                l_res = ''
                r_res = ''
                if type(child) == str:
                    # res += '(' + child + ') < '
                    if not filters['node_order'] or indices[i_child][i_new_result] < self.children_split:
                        l_res += child + ' < '
                    else:
                        r_res += ' > ' + child
                else:
                    if filters['node_order']:
                        new_child = child
                    else:
                        new_child = sorted(child)
                    for i_el, el in enumerate(new_child):
                        # res += '(' + el + ') < '
                        if not filters['node_order'] or indices[i_child][i_el] < self.children_split:
                            l_res += el + ' < '
                        else:
                            r_res += ' > ' + el
                merged_results.append('(' + l_res + new_result + r_res + ')')
        return merged_results

    @staticmethod
    def create_output_left_children(left_children, new_results, filters):
        merged_results = []
        for child in left_children:
            for new_result in new_results:
                res = ''
                if type(child) == str:
                    # res += '(' + child + ') < '
                    res += child + ' < '
                else:
                    if filters['node_order']:
                        new_child = child
                    else:
                        new_child = sorted(child)
                    for el in new_child:
                        # res += '(' + el + ') < '
                        res += el + ' < '
                merged_results.append('(' + res + new_result + ')')
        return merged_results

    @staticmethod
    def create_output_right_children(new_results, right_children, filters):
        merged_results = []
        for child in right_children:
            for new_result in new_results:
                res = ''
                if type(child) == str:
                    res += ' > ' + child
                    # res += ' > (' + child + ')'
                else:
                    if filters['node_order']:
                        new_child = child
                    else:
                        new_child = sorted(child)
                    for el in new_child:
                        res += ' > ' + el
                        # res += ' > (' + el + ')'
                merged_results.append('(' + new_result + res + ')')
                # merged_results.append(new_result + ' > (' + child + ')')
        return merged_results

    @staticmethod
    def create_answers(separated_answers, separated_answers_architecture, answer_length, filters):
        # TODO
        # node_order = False
        partly_built_trees = [[None] * answer_length]
        partly_built_trees_architecture = [[None] * answer_length]
        partly_built_trees_architecture_indices = [[None] * answer_length]
        built_trees = []
        built_trees_architecture = []
        built_trees_architecture_indices = []
        # iterate over children first, so that new partly built trees are added only after all results of specific
        # child are added
        for child_i in range(len(separated_answers[0])):
            new_partly_built_trees = []
            new_partly_built_trees_architecture = []
            new_partly_built_trees_architecture_indices = []
            # iterate over answers parts
            for answer_part_i in range(len(separated_answers)):
                # necessary because some parts do not pass filters and are not added
                # if child_i < len(separated_answers[answer_part_i]) and separated_answers[answer_part_i][child_i]:
                if separated_answers[answer_part_i][child_i]:
                    for tree_part_i, tree_part in enumerate(partly_built_trees):
                        # if tree_part[answer_part_i] equals None add new element in its place
                        if not tree_part[answer_part_i]:
                            new_tree_part = copy(tree_part)
                            new_tree_part_architecture = copy(partly_built_trees_architecture[tree_part_i])
                            new_tree_part_architecture_indices = copy(partly_built_trees_architecture_indices[tree_part_i])
                            new_tree_part[answer_part_i] = separated_answers[answer_part_i][child_i][0]
                            new_tree_part_architecture[answer_part_i] = separated_answers_architecture[answer_part_i][child_i][0]
                            new_tree_part_architecture_indices[answer_part_i] = child_i
                            completed_tree_part = True
                            for val_i, val in enumerate(new_tree_part):
                                if not val:
                                    completed_tree_part = False
                            if completed_tree_part:
                                built_trees.append(new_tree_part)
                                built_trees_architecture.append(new_tree_part_architecture)
                                built_trees_architecture_indices.append(new_tree_part_architecture_indices)
                            else:
                                new_partly_built_trees.append(new_tree_part)
                                new_partly_built_trees_architecture.append(new_tree_part_architecture)
                                new_partly_built_trees_architecture_indices.append(new_tree_part_architecture_indices)

            partly_built_trees.extend(new_partly_built_trees)
            partly_built_trees_architecture.extend(new_partly_built_trees_architecture)
            partly_built_trees_architecture_indices.extend(new_partly_built_trees_architecture_indices)

        l_ordered_built_trees_architecture, l_ordered_built_trees, l_ordered_built_trees_index, unique_trees_architecture = [], [], [], []

        if built_trees:
            # sort 3 arrays by architecture indices
            temp_trees_index, temp_trees, temp_trees_architectures = (list(t) for t in zip(
                *sorted(zip(built_trees_architecture_indices, built_trees, built_trees_architecture))))

            # order outputs and erase duplicates
            # for tree, tree_architecture, tree_architecture_indice in zip(built_trees, built_trees_architecture, built_trees_architecture_indices):
            for tree, tree_architecture, tree_index in zip(temp_trees, temp_trees_architectures, temp_trees_index):
                new_tree_index, new_tree, new_tree_architecture = (list(t) for t in zip(*sorted(zip(tree_index, tree, tree_architecture))))
                # TODO check if inside new_tree_architecture in ordered_built_trees_architecture and if not append!
                is_unique = True
                for unique_tree in unique_trees_architecture:
                    already_in = True
                    for part_i in range(len(unique_tree)):
                        if unique_tree[part_i] != new_tree_architecture[part_i]:
                            already_in = False
                            break
                    if already_in:
                        is_unique = False
                        break

                if is_unique:
                    unique_trees_architecture.append(new_tree_architecture)
                    # if not filters['node_order']:
                    l_ordered_built_trees_architecture.append(new_tree_architecture)
                    l_ordered_built_trees.append(new_tree)
                    l_ordered_built_trees_index.append(new_tree_index)
                    # TODO NODE ORDER = FALSE
                    # else:
                    #
                    #     ordered_built_trees_architecture.append(tree_architecture)
                    #     ordered_built_trees.append(tree)
                # print("test")
        # for answer1_i, answer1 in enumerate(separated_answers):
        #     for answer2_i, answer2 in enumerate(separated_answers):
        #         if answer1_i != answer2_i:
        #             res, res_i = self.merge_answer(answer1, answer2, answer1_i, answer2_i)
        #             print('aaa')
        #
        # pass
        return l_ordered_built_trees, l_ordered_built_trees_architecture, l_ordered_built_trees_index


def create_output_string_form(tree):
    return tree.form.get_value()

def create_output_string_deprel(tree):
    return tree.deprel.get_value()

def create_output_string_lemma(tree):
    return tree.lemma.get_value()

def create_output_string_upos(tree):
    return tree.upos.get_value()

def create_output_string_xpos(tree):
    return tree.xpos.get_value()
