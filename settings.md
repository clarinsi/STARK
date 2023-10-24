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
The obligatory `--fixed` parameter allows the users to specify whether they consider the order of the nodes in the tree to be a distinctive feature of the tres (value `yes`) or not (value `no`). For example, if our input treebank consisted of the sentences ‘_John gave the apple to Mary_’ and ‘_John the apple gave to Mary_’ (an odd example in English but typical in languages with free word order), using the `yes` option would extract the '_gave > apple_' and '_apple < gave_' as two distinct trees, while the `no` option would consider them as two instances of the same tree ('_gave > apple_'). 

Note that each of the two options is associated with specific formatting of the output. When choosing the `fixed=yes` option, the tree description in the first column reflects the word order of the nodes on the surface (e.g. _(seemingly < easy) < example_'), which is also explicitely given in an additional column (e.g. _ABC_ for nodes A, B and C). On the other hand, when choosing the `fixed=no` option, the description of the tree in the first column is order-agnostic, with heads always preceding the dependents, i.e. all the arrows always pointing to the right (e.g. '_example > (easy > seemingly)_'.


## Restriction to specific structures
In contrast to the obligatory settings above specifying the criteria for defining the _types_ of trees to be extracted, STARK also allows the users to restrict the extraction procedure to _specific_ trees through the three options presented below.

The optional `--labels` parameter defines a list of dependency relations that are allowed to occur in the trees to be extracted (i.e. a whitelist subset of all possible dependency labels) in the form of a list, separated by the '|' operator. For example, specifying `obj|iobj|nsubj` would only extract trees featuring these three relations and ignore all others.

Similarly, the optional `--root` parameter allows the users to define specific constraints on the root node (i.e. the word that all other words in the tree depend on) in the form of attribute-value pairs specifying its lexical or grammatical features. For example, `upos=NOUN` would only return trees with nouns as heads (nominal phrases) and discard trees spanning from other part-of-speech categories.

Finally, the optional `--query` parameter allows the users to define a specific tree structure to be extracted by using the DepSearch query language. For example, the query `upos=NOUN >amod (_ >advmod _)` would return nouns that govern an adjectival modifier modified by an adverbial modifier, e.g. trees of the type '_seemingly easy example_'. Note that the query language requires the attributes to be written in full (e.g. _upos=NOUN_, _form=give_)

## Statistics
By default, STARK produces a list of trees with the absolute frequency (raw count) and the relative frequency (normalized count per million tokens) of the trees in the input treebank. In addition, two optional types of statistics can also be computed in the output to help identify compelling syntactic phenomena.

The optional `--association_measures` parameter (value `yes`) produces information on the strength of statistical association between the nodes of the tree by computing several common association scores (MI, MI3 , Dice, logDice, t-score, simple-LL). This is a particularly useful feature for treebank-driven collocation extraction and lexical analysis.

In addition, STARK can also be used to identify key or statistically significant phenomena in the input treebank by comparing its frequency to that of another, so-called reference treebank. This is triggered by using the optional `--compare` parameter which takes the name of the reference treebank as input (e.g. `second_treebank.conllu`) to compute several common keyness scores (LL, BIC, log ratio, odds ratio and %DIFF).

## Limiting the size of the output
To limit the number of trees in the output file, the optional `--frequency_threshold` parameter can be used to limit the extraction to trees occurring above a given threshold by specifying the minimal absolute frequency of the tree in the treebank (e.g. `5` to to limit the search to trees occurring 5 or more times).

Similarly, the optional `--max_lines` parameter defines the maximum number of trees (lines) in the output frequency-ranked list. For example, value `100` returns only the 100 most frequent trees matching the input criteria.

## Visualising the trees online
In addition to the default description of the trees featured in the first column of the output, which is based on the DepSearch query language and is relatively easy to read (e.g. _ADJ <amod NOUN_), STARK can also produce two alternative ways of describing a tree that also enable the users to visualisize specific instances of the trees in related treebank-browsing services.

First, the optional `--depsearch` parameter (value `yes`) produces trees in accordance with the DepSearch query language (e.g. _NOUN >amod ADJ_) used by the SETS online service, which, unfortunately, is no longer maintained.

Second, the optional `--grew_match` parameter (value `yes`) produces trees in accordance with the [Grew]([https://grew.fr/grew_match/help/](https://grew.fr/doc/request/) query language (e.g. '_pattern {A [upos="NOUN"]; B [upos="ADJ"]; A -[amod]-> B }_') used by [Grew-match](https://universal.grew.fr/) online service which supports browsing the latest collections of UD treebanks available in more than 240 languages. 

If the name of the input treebank begins with the standard declaration of the language code and the treebank name (e.g. `en_gum-ud`, `fr_rhapsodie-ud`, `sl_ssj-ud` ...), the `grew_match=yes` option will also produce direct URL links to the instances of the tree in the latest version of the given input treebank (e.g. [this-link](this-url)  for the '_ADJ <amod NOUN_' case at hand).


