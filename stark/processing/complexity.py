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

import math

_CLAUSE_DEPRELS = frozenset({"csubj", "ccomp", "xcomp", "advcl", "acl", "conj", "parataxis"})
_T_UNIT_DEPRELS = frozenset({"conj", "parataxis"})
_EXCLUDED_DEPRELS = frozenset({"punct", "root"})


def get_complexity_data(repr_tree):
    """
    Compute per-occurrence syntactic complexity metrics for a matched subtree.

    Performs a single DFS over the RepresentationTree, collecting arc endpoint
    positions and node locations (for MDD/NDD, in both the original-sentence
    and locally re-indexed variants), node count, max depth, and clause/T-unit
    counts.

    Intended to be called once per matched occurrence inside
    postprocess_query_results(); results are accumulated via
    accumulate_complexity_sum() into summary.representation_trees and
    averaged at write time by Writer.get_complexity_measures().

    Metrics follow calculate_metrics.py (SyntComplex), adapted for subtrees:
      - MDD-mean      : mean |head_pos - dep_pos| over non-punct arcs, using
                        each token's position in the original sentence
      - MDD-structure : same, but using positions re-indexed locally to the
                        isolated subtree (1, 2, 3, ... in surface order),
                        independent of where the subtree sits in the sentence
      - NDD-mean / NDD-structure : |log(MDD / sqrt(root_pos * n_arcs))|
                        (Jiang & Liu 2015), using the matching root_pos
                        (sentence position or local rank) for each variant
      - max_depth : deepest level in the subtree (root = 1)
      - n_nodes   : total number of nodes in the subtree (incl. punct)
      - n_clauses : 1 + verbal clause-introducing dependents within the subtree
      - n_t_units : 1 + verbal conj/parataxis dependents within the subtree

    NDD, n_clauses and n_t_units are only meaningful when the subtree root is
    the sentence's actual root (deprel == 'root') — a clause/T-unit count or a
    root-position-based distance metric isn't well-defined for an arbitrary
    fragment of a sentence. They are set to None otherwise; callers (the
    writers) render that as the existing 'n/a' placeholder.

    Note: has_cop_child only inspects children present in the extracted subtree;
    a copula outside the matched pattern will not be counted.

    :param repr_tree: RepresentationTree instance for one matched occurrence
    :return: dict with keys is_root, mdd_mean, mdd_structure, max_depth,
             n_nodes, ndd_mean, ndd_structure, n_clauses, n_t_units
             (the last four are None when not is_root)
    """
    is_root = repr_tree.node.node.deprel == 'root'
    arcs, locations, max_depth, n_nodes, n_clauses, n_t_units = _traverse_subtree(repr_tree)

    # MDD-mean — mean dependency distance over non-punct arcs, original positions
    mdd_mean = _mean_dependency_distance(arcs)

    # MDD-structure — same, but with positions re-indexed locally within the
    # isolated subtree (1, 2, 3, ... in surface order), so the value depends
    # only on the subtree's shape, not on where it sits in the sentence.
    rank = {loc: i + 1 for i, loc in enumerate(sorted(set(locations)))}
    structure_arcs = [(rank[p], rank[c]) for p, c in arcs]
    mdd_structure = _mean_dependency_distance(structure_arcs)

    n_arcs = len(arcs)
    if is_root:
        root_pos = repr_tree.node.location
        ndd_mean = _normalized_dependency_distance(mdd_mean, root_pos, n_arcs)
        ndd_structure = _normalized_dependency_distance(mdd_structure, rank[root_pos], n_arcs)
    else:
        ndd_mean = None
        ndd_structure = None
        n_clauses = None
        n_t_units = None

    return {
        'is_root': is_root,
        'mdd_mean': mdd_mean,
        'mdd_structure': mdd_structure,
        'max_depth': max_depth,
        'n_nodes': n_nodes,
        'ndd_mean': ndd_mean,
        'ndd_structure': ndd_structure,
        'n_clauses': n_clauses,
        'n_t_units': n_t_units,
    }


def init_complexity_sum():
    """Zeroed running-sum accumulator for one representation_trees entry."""
    return {
        'mdd_mean': 0.0,
        'mdd_structure': 0.0,
        'max_depth': 0,
        'ndd_mean': 0.0,
        'ndd_structure': 0.0,
        'n_clauses': 0,
        'n_t_units': 0,
        'count_root': 0,
    }


def accumulate_complexity_sum(complexity_sum, complexity):
    """
    Adds one occurrence's complexity dict (from get_complexity_data) into a
    running-sum accumulator (from init_complexity_sum).

    mdd_mean/mdd_structure/max_depth are always defined and accumulated
    against the entry's total occurrence count. ndd_mean/ndd_structure/
    n_clauses/n_t_units are only defined for root occurrences, so they're
    accumulated against a separate 'count_root' counter.
    """
    complexity_sum['mdd_mean'] += complexity['mdd_mean']
    complexity_sum['mdd_structure'] += complexity['mdd_structure']
    complexity_sum['max_depth'] += complexity['max_depth']
    if complexity['is_root']:
        complexity_sum['count_root'] += 1
        complexity_sum['ndd_mean'] += complexity['ndd_mean']
        complexity_sum['ndd_structure'] += complexity['ndd_structure']
        complexity_sum['n_clauses'] += complexity['n_clauses']
        complexity_sum['n_t_units'] += complexity['n_t_units']


def _traverse_subtree(repr_tree):
    """DFS collecting non-punct arc endpoints, all node locations, max depth, and clause/T-unit counts."""
    arcs = []           # (parent_sentence_pos, child_sentence_pos) — punct excluded
    locations = []      # every node's sentence position, for local re-indexing
    counts = {'n_nodes': 0, 'n_clauses': 1, 'n_t_units': 1}  # root counts as the main predication

    def _visit(rtn, depth):
        counts['n_nodes'] += 1
        locations.append(rtn.node.location)
        local_max = depth
        for child in rtn.children:
            deprel = child.node.node.deprel
            if deprel not in _EXCLUDED_DEPRELS:
                arcs.append((rtn.node.location, child.node.location))
            is_verbal = child.node.node.upos == "VERB" or _has_cop_child(child)
            if deprel in _CLAUSE_DEPRELS and is_verbal:
                counts['n_clauses'] += 1
            if deprel in _T_UNIT_DEPRELS and is_verbal:
                counts['n_t_units'] += 1
            local_max = max(local_max, _visit(child, depth + 1))
        return local_max

    max_depth = _visit(repr_tree, 1)
    return arcs, locations, max_depth, counts['n_nodes'], counts['n_clauses'], counts['n_t_units']


def _has_cop_child(rtn):
    """Return True if any direct child in the subtree carries deprel 'cop'."""
    return any(child.node.node.deprel == "cop" for child in rtn.children)


def _mean_dependency_distance(arcs):
    return sum(abs(p - c) for p, c in arcs) / len(arcs) if arcs else 0.0


def _normalized_dependency_distance(mdd_val, root_pos, n_arcs):
    if mdd_val > 0 and root_pos > 0 and n_arcs > 0:
        return abs(math.log(mdd_val / math.sqrt(root_pos * n_arcs)))
    return 0.0
