# STARK settings explained

Below is a list of customizable settings that can be used to define the type of trees to be extracted and the associated information in the output. 

|General | Tree specification | Tree restrictions | Statistics | Other |
| --- | --- | --- | --- | --- | 
| [input](#general-settings) | [size](#tree-size) | [labels](#restriction-to-specific-structures) | [association_measures](#statistics) | [max_lines](#limiting-the-size-of-the-output) |
| [output](#general-settings) | [node_type](#node-type) | [root](#restriction-to-specific-structures) | [compare](#statistics) | [frequency_threshold](#limiting-the-size-of-the-output) |
| [internal_saves](#general-settings) | [complete](#incomplete-trees) | [query](#restriction-to-specific-structures) |  | [grew_match](#visualising-the-trees-online) |
| [cpu_cores](#general-settings) | [labeled](#unlabeled-relations) |  |  | [depsearch](#visualising-the-trees-online) |
| | [fixed](#word-order) |  |  |  |

## General settings
The `--input` parameter defines the location of the input file or directory, i.e. one or more files in the `.conllu` format. The tool is primarily aimed at processing corpora based on the [Universal Dependencies](https://universaldependencies.org/) annotation scheme, but can also be used for any other dependency-parsed corpus complying with the CONLL-U format.

Regardless of the input settings, STARK produces a single tab-separated file (.tsv) as output, the name and the location of which is defined using the `--output` setting.

Performance-related settings include the specification of the folder for internal storage during processing (`--internal_saves`) and the number of processors used (`--cpu_core`), although most users will not need to change these. 

## Tree size

The obligatory `--size` parameter is defined as the number of tokens (typically words) in the trees to be extracted, which can either be specified as an integer number (e.g. `1`, `2`, `3` … ) or a range (e.g. `2-5`). Note that trees containing a higher number of tokens may necessitate additional processing time.

## Node type
The obligatory `--node_type` parameter specifies which characteristics of the tokens should be considered when extracting and counting the trees: word form (value `form`, e.g. _went_), lemma (`lemma`, e.g. _go_), part-of-speech tag (`upos`, e.g. _VERB_), morphological features (`feats`, e.g. _Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin_), language-specific tag (`xpos`, e.g. _VBD_), dependency role (`deprel`, e.g. _root_) or a combination of them signalled by the '+' operator (e.g. `lemma+upos`). For example, if the option `form` returns trees of the type '_Mary <nsubj went_', the option `upos` returns trees of the type '_PROPN <nsubj VERB_'.

## (In)complete trees
The obligatory `--complete` parameter defines whether STARK, for a given tree size, should only extract only complete trees encompassing the head and all its (in)direct dependants (value `yes`), or all possible subtrees spanning from the head, i.e. all possible combinations of the head and its dependants (value `no`). Naturally, the second option places a significantly higher computational demand and should be used with caution.

## (Un)labeled relations
The obligatory `labeled` parameter specifies whether trees should be differentiated based on the syntactic relations (dependency labels) between the nodes of the tree (value `yes`, or not (value `no`). For example, if the first option differentiates between trees '_NOUN <nsubj VERB_' and '_NOUN <obj VERB_', the second option considers them as the instances of the same, '_NOUN < VERB_' tree.


## Word order
The obligatory `--fixed` parameter allows the users to specify whether they consider the order of the nodes in the tree to be a distinctive feature of the tres (value `yes`) or not (value `no`). For example, if our input treebank consisted of the sentences ‘_John gave the apple to Mary_’ and ‘_John the apple gave to Mary_’ (an odd example in English but typical in languages with free word order), using the `yes` option would extract the '_gave > apple_' and '_apple < gave_' as two distinct trees, while the `no` option would consider them as two instances of the same tree. 

## Restriction to specific structures
In contrast to the obligatory settings above specifying the criteria for defining the _types_ of trees to be extracted, STARK also allows the users to restrict the extraction procedure to specific groups of trees through the tree options presented below.

The optional `--labels` parameter defines a list of dependency relations that are allowed to occur in the trees to be extracted (i.e. a whitelist subset of all possible dependency labels) in the form of a list, separated by the '|' operator. For example, specifying `obj|iobj|nsubj` would only extract trees featuring these three relations and ignore all others.

Similarly, the optional `--root` parameter allows the users to define specific constraints on the root node (i.e. the word that all other words in the tree depend on) in the form of attribute-value pairs specifying its lexical or grammatical features. For example, `upos=NOUN` would only return trees with nouns as heads (nominal phrases) and discard trees spanning from other part-of-speech categories.

Finally, the optional `--query` parameter allows the users to define a specific tree structure to be extracted by using the DepSearch query language. For example, the query `NOUN >amod (_ >advmod _)` would return nouns that govern an adjectival modifier modified by an adverbial modifier, e.g. trees of the type '_seemingly easy example_'. 

## Statistics

## Limiting the size of the output

## Visualising the trees online
