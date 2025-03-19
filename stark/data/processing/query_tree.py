# Copyright 2024 CJVT
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

from copy import copy

from stark.data.representation.node import RepresentationNode
from stark.data.representation.query_tree import QueryRepresentationTree
from stark.data.processing.tree import Tree
from stark.processing.filters import Filter


class QueryTree(Tree):
    def __init__(self, index, form, lemma, upos, xpos, deprel, head, feats_detailed, token_misc, document, summary):
        super().__init__(index, form, lemma, upos, xpos, deprel, head, feats_detailed, token_misc, document, summary)

    def get_subtrees(self, permanent_query_trees, temporary_query_trees, filters):
        """

        :param filters:
        :param permanent_query_trees:
        :param temporary_query_trees:
        """

        # list of all children queries grouped by parent queries
        all_query_indices = []

        active_permanent_query_trees = []
        for permanent_query_tree in permanent_query_trees:
            if (self._fits_static_requirements(permanent_query_tree, filters)
                    and self._fits_permanent_requirements(filters)):
                active_permanent_query_trees.append(permanent_query_tree)
                if 'children' in permanent_query_tree:
                    all_query_indices.append((permanent_query_tree['children'], True))
                    # r_all_query_indices.append((permanent_query_tree['r_children'], True))

        active_temporary_query_trees = []
        successful_temporary_queries = []
        for i, temporary_query_tree in enumerate(temporary_query_trees):
            if (self._fits_static_requirements(temporary_query_tree, filters)
                    and self._fits_temporary_requirements(filters)):
                active_temporary_query_trees.append(temporary_query_tree)
                successful_temporary_queries.append(i)
                if 'children' in temporary_query_tree:
                    all_query_indices.append((temporary_query_tree['children'], False))

        partial_subtrees, complete_answers = QueryTree._get_all_query_indices(len(temporary_query_trees),
                                                                         len(permanent_query_trees),
                                                                         permanent_query_trees,
                                                                         all_query_indices, self.children,
                                                                         filters)

        merged_partial_answers = []
        i_question = 0
        # i_child is necessary, because some queries may be answered at the beginning and were not passed to children.
        # i_child is used to point where we are inside answers
        i_answer = 0
        # go over all permanent and temporary query trees
        while i_question < len(active_permanent_query_trees) + len(active_temporary_query_trees):
            # permanent query trees always have left and right child
            i_answer = self._order_dependent_queries(active_permanent_query_trees, active_temporary_query_trees,
                                                    partial_subtrees, merged_partial_answers,
                                                    i_question, i_answer, filters)

            i_question += 1

        for i in range(len(active_permanent_query_trees)):
            # erase first and last brackets when adding new query result
            add_subtree = [subtree.ignore_labels(filters) for subtree in merged_partial_answers[i]]
            complete_answers[i].extend(add_subtree)

        # answers to valid queries
        partial_answers = [[] for _ in range(len(temporary_query_trees))]
        for inside_i, outside_i in enumerate(successful_temporary_queries):
            partial_answers[outside_i] = merged_partial_answers[
                len(active_permanent_query_trees) + inside_i]

        return partial_answers, complete_answers

    def _fits_static_requirements_feats(self, query_tree):
        if 'feats_detailed' not in query_tree:
            return True

        for feat in query_tree['feats_detailed'].keys():
            if (feat not in self.feats_detailed or
                    query_tree['feats_detailed'][feat] != next(iter(self.feats_detailed[feat].values()))):
                return False

        return True

    def _fits_permanent_requirements(self, filters):
        return Filter.check_root_whitelist(self.form, self.lemma, self.upos,
                                           self.feats, self.deprel, self.misc, filters)

    def _fits_temporary_requirements(self, filters):
        return Filter.check_label_whitelist(self.deprel, filters)

    def _fits_static_requirements(self, query_tree, filters):
        return Filter.check_query_tree(query_tree, self.form, self.lemma, self.upos,
                                       self.xpos, self.feats, self.deprel,
                                       self.children, filters)


    @staticmethod
    def _merge_results3(child, new_results, filters):
        if filters['node_order']:
            new_child = child

        else:
            new_child = sorted(child, key=lambda x: x[0].get_key(filters))

        children_groups = []

        for i_answer, answer in enumerate(new_child):
            children_groups = QueryTree._create_children_groups(children_groups, [[answer_part] for answer_part in answer])

        results = []
        for result in new_results:
            for children in children_groups:
                new_result = copy(result)
                new_result.set_children(children)
                results.append(new_result)

        return results

    @staticmethod
    def _get_all_query_indices(temporary_query_nb, permanent_query_nb, permanent_query_trees, all_query_indices,
                               children, filters):
        partial_answers = [[] for _ in range(permanent_query_nb + temporary_query_nb)]
        complete_answers = [[] for _ in range(permanent_query_nb)]

        # list of pairs (index of query in group, group of query)
        child_queries = [all_query_indice[0] for all_query_indice in all_query_indices]

        answers_lengths = [len(query) for query in child_queries]

        child_queries_flatten = [query_part for query in child_queries for query_part in query]

        all_new_partial_answers = [[] for _ in child_queries_flatten]

        child_queries_flatten_dedup = []
        child_queries_flatten_dedup_indices = []
        for query_part in child_queries_flatten:
            try:
                index = child_queries_flatten_dedup.index(query_part)
            except ValueError:
                index = len(child_queries_flatten_dedup)
                child_queries_flatten_dedup.append(query_part)

            child_queries_flatten_dedup_indices.append(index)

        # ask children all queries/partial queries
        for child in children:
            # obtain children results
            new_partial_answers_dedup, new_complete_answers = child.get_subtrees(permanent_query_trees,
                                                                                 child_queries_flatten_dedup,
                                                                                 filters)

            assert len(new_partial_answers_dedup) == len(child_queries_flatten_dedup)

            # duplicate results again on correct places
            for i, flattened_index in enumerate(child_queries_flatten_dedup_indices):
                all_new_partial_answers[i].append(new_partial_answers_dedup[flattened_index])

            for i in range(len(new_complete_answers)):
                # TODO add order rearagement (TO KEY)
                complete_answers[i].extend(new_complete_answers[i])

        # merge answers in appropriate way
        i = 0
        # iterate over all answers per queries
        for answer_i, answer_length in enumerate(answers_lengths):
            # iterate over answers of query
            partial_answers[answer_i] = QueryTree._create_answers(all_new_partial_answers[i:i + answer_length],
                                                             answer_length, filters)
            i += answer_length

        return partial_answers, complete_answers

    def _order_dependent_queries(self, active_permanent_query_trees, active_temporary_query_trees, partial_subtrees,
                                 merged_partial_subtrees, i_query, i_answer, filters):
        node = RepresentationNode(self, self.index, filters['create_output_string_functs'])

        if i_query < len(active_permanent_query_trees):
            if 'children' in active_permanent_query_trees[i_query]:
                merged_partial_subtrees.append(
                    self._create_output_children(partial_subtrees[i_answer],
                                                 [QueryRepresentationTree(node, [], filters)], filters))
                i_answer += 1
            else:
                merged_partial_subtrees.append([QueryRepresentationTree(node, [], filters)])
        else:
            if 'children' in active_temporary_query_trees[i_query - len(active_permanent_query_trees)]:
                merged_partial_subtrees.append(
                    self._create_output_children(partial_subtrees[i_answer],
                                                 [QueryRepresentationTree(node, [], filters)], filters))
                i_answer += 1
            else:
                merged_partial_subtrees.append([QueryRepresentationTree(node, [], filters)])
        return i_answer

    @staticmethod
    def _create_children_groups(left_parts, right_parts):
        if not left_parts:
            return right_parts

        if not right_parts:
            return left_parts

        all_children_group_possibilities = []
        for left_part in left_parts:
            for right_part in right_parts:
                new_part = copy(left_part)
                new_part.extend(right_part)
                all_children_group_possibilities.append(new_part)
        return all_children_group_possibilities

    def _create_output_children(self, children, new_results, filters):
        merged_results = []
        for i_child, child in enumerate(children):
            merged_results.extend(self._merge_results3(child, new_results, filters))
        return merged_results

    @staticmethod
    def _create_answers(separated_answers, answer_length, filters):
        partly_built_trees = [[None] * answer_length]
        partly_built_trees_architecture_indices = [[None] * answer_length]
        built_trees = []
        built_trees_architecture_indices = []

        # iterate over children first, so that new partly built trees are added only after all results of specific
        # child are added
        for child_i in range(len(separated_answers[0])):
            new_partly_built_trees = []
            new_partly_built_trees_architecture_indices = []
            # iterate over answers parts
            for answer_part_i in range(len(separated_answers)):
                # necessary because some parts do not pass filters and are not added
                if separated_answers[answer_part_i][child_i]:
                    for tree_part_i, tree_part in enumerate(partly_built_trees):
                        if not tree_part[answer_part_i]:
                            new_tree_part = copy(tree_part)
                            new_tree_part_architecture_indices = (
                                copy(partly_built_trees_architecture_indices[tree_part_i]))
                            new_tree_part[answer_part_i] = separated_answers[answer_part_i][child_i]
                            new_tree_part_architecture_indices[answer_part_i] = child_i
                            completed_tree_part = True
                            for val_i, val in enumerate(new_tree_part):
                                if not val:
                                    completed_tree_part = False
                            if completed_tree_part:
                                built_trees.append(new_tree_part)
                                built_trees_architecture_indices.append(new_tree_part_architecture_indices)
                            else:
                                new_partly_built_trees.append(new_tree_part)
                                new_partly_built_trees_architecture_indices.append(new_tree_part_architecture_indices)
                        else:
                            # pass over repetitions of same words
                            pass

            partly_built_trees.extend(new_partly_built_trees)
            partly_built_trees_architecture_indices.extend(new_partly_built_trees_architecture_indices)

        l_ordered_built_trees, unique_trees_architecture = [], []

        if built_trees:
            # sort 3 arrays by architecture indices
            temp_trees_index, temp_trees = (list(t) for t in zip(
                *sorted(zip(built_trees_architecture_indices, built_trees))))

            # order outputs and erase duplicates
            for tree, tree_index in zip(temp_trees, temp_trees_index):
                new_tree_index, new_tree = (list(t) for t in zip(*sorted(zip(tree_index, tree))))
                is_unique = True
                for unique_tree in unique_trees_architecture:
                    already_in = True
                    for part_i in range(len(unique_tree)):
                        if (len(unique_tree[part_i]) != len(new_tree[part_i])
                                or any(unique_tree[part_i][i_unique_part].get_order_key(filters) !=
                                       new_tree[part_i][i_unique_part].get_order_key(filters)
                                       for i_unique_part in range(len(unique_tree[part_i])))):
                            already_in = False
                            break
                    if already_in:
                        is_unique = False
                        break

                if is_unique:
                    unique_trees_architecture.append(new_tree)
                    l_ordered_built_trees.append(new_tree)
        return l_ordered_built_trees
