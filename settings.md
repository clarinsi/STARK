# STARK settings explained

Below is a list of customizable settings that can be used to define the type of trees to be extracted and the associated information in the output. 

|General | Tree specification | Tree restrictions | Statistics | Other |
| --- | --- | --- | --- | --- | 
| [input](#general-settings) | [size](#tree-size) | [labels](#restrict-search-to-specific-labels) | [association_measures](#association) | [max_lines](#limiting-the-size-of-the-output) |
| [output](#general-settings) | [node_type](#node-type) | [root](#restrict-search-to-specific-nodes) | [compare](#keyness) | [frequency_threshold](#limiting-the-size-of-the-output) |
| [internal_saves](#general-settings) | [complete](#incomplete-trees) | [query](#restrict-search-to-specific-trees) |  | [grew_match](#grew-match) |
| [cpu_cores](#general-settings) | [labeled](#unlabeled-relations) |  |  | [depsearch](#depsearch-based-services) |
| | [fixed](#word-order) |  |  |  |

## General settings
The `--input` parameter defines the location of the input file or directory, i.e. one or more files in the `.conllu` format. The tool is primarily aimed at processing corpora based on the [Universal Dependencies](https://universaldependencies.org/) annotation scheme, but can also be used for any other dependency-parsed corpus complying with the CONLL-U format. The only condition is that there is exactly one root node per sentence (named _root_). 

Regardless of the input settings, STARK produces a single tab-separated file (.tsv) as output, the name and the location of which is defined using the `--output` setting.

Performance-related settings include the specification of the folder for internal storage during processing (`--internal_saves`) and the number of processors used (`--cpu_core`), although most users will not need to change these. 

## Tree specification

### Tree size

The obligatory `--size` parameter is defined as the number of tokens (typically words) in the trees to be extracted, which can either be specified as an integer number (e.g. _1, 2, 3_ … ) or a range (e.g. _2-5_). Note that trees containing a higher number of tokens may necessitate additional processing time.

### Node type
The obligatory `--node_type` parameter specifies which characteristics of the tokens should be considered when extracting and counting the trees: word form (value _form_, e.g. 'went'), lemma (_lemma_, e.g. 'go'), part-of-speech tag (_upos_, e.g. 'VERB'), morphological features (_feats_, e.g. 'Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin'), language-specific tag (_xpos_, e.g. 'VBD'), dependency role (_deprel_, e.g. 'root') or a combination of them signalled by the '+' operator (e.g. _lemma+upos_). For example, while the option _form_ returns trees of the type 'Mary <nsubj went', the option _upos_ returns trees of the type 'PROPN <nsubj VERB'.

### (In)complete trees
The obligatory `--complete` parameter defines whether STARK, for a given tree size, should only extract only complete trees encompassing the head and all its (in)direct dependants (value _yes_), or all possible subtrees spanning from the head, i.e. all possible combinations of the head and its dependants (value _no_). Naturally, the second option places a significantly higher computational demand and should be used with caution.

### (Un)labeled relations
The obligatory `--labeled` parameter specifies whether trees should be differentiated based on the syntactic relations (dependency labels) between the nodes of the tree (value _yes_), or not (value _no_). For example, if the first option differentiates between trees 'NOUN <nsubj VERB' and 'NOUN <obj VERB', the second option considers them as two instances of the same tree, i.e. 'NOUN < VERB'.

### Word order
The obligatory `--fixed` parameter allows the users to specify whether they consider the order of the nodes in the tree to be a distinctive feature of the tres (value _yes_) or not (value _no_). For example, if the input treebank contained sentences ‘_John gave the apple to Mary_’ and ‘_John the apple gave to Mary_’ (an odd example in English but typical in languages with free word order), using the _yes_ option would extract the 'gave > apple' and 'apple < gave' as two distinct trees, while the _no_ option would consider them as two instances of the same tree, i.e. 'gave > apple'. 

Note that each of the two options is associated with specific formatting of the tress in the output. When choosing the _fixed=yes_ option, the tree description in the first column reflects the word order of the nodes on the surface (e.g. '(seemingly < easy) < example'). On the other hand, when choosing the _fixed=no_ option, the description of the tree in the first column is order-agnostic, with heads always preceding their dependents, i.e. all the arrows always pointing to the right (e.g. 'example > (easy > seemingly)'. The latter description can also be produced regardless of the word order setting, by using the `--depsearch` option (value _yes_), which, for example, might be useful for users investigating word order variation. 

## Restriction to specific structures
In contrast to the obligatory settings above specifying the criteria for defining the _types_ of trees to be extracted, STARK also allows the users to restrict the extraction procedure to _specific_ trees through the three options presented below.

### Restrict search to specific labels
The optional `--labels` parameter defines a list of dependency relations that are allowed to occur in the trees to be extracted (i.e. a whitelist subset of all possible dependency labels) in the form of a list, separated by the '|' operator. For example, specifying _=obj|iobj|nsubj_ would only extract trees featuring these three relations and ignore all others.

### Restrict search to specific nodes
Similarly, the optional `--root` parameter allows the users to define specific constraints on the root node (i.e. the word that all other words in the tree depend on) in the form of attribute-value pairs specifying its lexical or grammatical features. For example, _upos=NOUN_ would only return trees with nouns as heads (nominal phrases) and discard trees spanning from other part-of-speech categories.

### Restrict search to specific trees
Finally, the optional `--query` parameter allows the users to define a specific tree structure to be extracted by using the DepSearch query language. For example, the query _upos=NOUN >amod (_ >advmod _)_ would return nouns that govern an adjectival modifier modified by an adverbial modifier, e.g. trees of the type '_seemingly easy example_'. Note that the query language requires the attributes to be written in full (e.g. _upos=VERB_, _form=went_, _L=go_).

## Statistics
By default, STARK produces a list of trees with the absolute frequency (raw count) and the relative frequency (normalized count per million tokens) of the trees in the input treebank. In addition, two optional types of statistics can also be computed in the output to help identify compelling syntactic phenomena.

### Association
The optional `--association_measures` parameter (value _yes_) produces information on the strength of statistical association between the nodes of the tree by computing several common association scores (MI, MI3 , Dice, logDice, t-score, simple-LL). This is a particularly useful feature for treebank-driven collocation extraction and lexical analysis.

### Keyness
In addition, STARK can also be used to identify key or statistically significant phenomena in the input treebank by comparing its frequency to that of another, so-called reference treebank. This is triggered by using the optional `--compare` parameter which takes the name of the second, reference treebank as input (e.g. _sl_ssj-ud-dev.conllu_) to compute the frequencies in both treebanks and compare them using several common keyness scores (LL, BIC, log ratio, odds ratio and %DIFF). This feature is particularly useful for research on language- or genre-specific syntactic phenomena.

## Limiting the size of the output
To limit the number of trees in the output file, the optional `--frequency_threshold` parameter can be used to limit the extraction to trees occurring above a given threshold by specifying the minimal absolute frequency of the tree in the treebank (e.g. _5_ to to limit the search to trees occurring 5 or more times).

Similarly, the optional `--max_lines` parameter defines the maximum number of trees (lines) in the output frequency-ranked list. For example, value _100_ returns only the top-100 most frequent trees matching the input criteria.

## Visualising the trees online
In addition to the [default description of the trees](README.md#description-of-tree-structure) featured in the first column of the output, which is based on the DepSearch query language and is relatively easy to read (e.g. 'ADJ <amod NOUN'), STARK can also produce two alternative ways of describing a tree that also enable the users to visualisize specific instances of the trees in related treebank-browsing services.

### Grew-match
First, the optional `--grew_match` parameter (value _yes_) produces trees in accordance with the [Grew](https://grew.fr/doc/request/) query language (e.g. 'pattern {A [upos="NOUN"]; B [upos="ADJ"]; A -[amod]-> B }') used by [Grew-match](https://universal.grew.fr/) online service which supports browsing the latest collections of UD treebanks available in more than 240 languages. 

If the name of the input treebank begins with the standard declaration of the language code and the treebank name (e.g. _en_gum-ud..._, _fr_rhapsodie-ud..._, _sl_ssj-ud..._), the _grew_match=yes_ option will also produce direct URL links to the instances of the tree in the latest version of the given input treebank (e.g. [this URL](http://universal.grew.fr/?corpus=UD_English-GUM&request=pattern%20%7BB%20%5Bupos%3DNOUN%5D%3B%20A%20%5Bupos%3DADJ%5D%3B%20B%20-%5Bamod%5D-%3E%20A%3B%20B%20%3E%3E%20A%7D) for the 'ADJ <amod NOUN' case at hand).

### DepSearch-based services
Second, the optional `--depsearch` parameter (value _yes_) produces trees in accordance with the [DepSearch query language](https://orodja.cjvt.si/drevesnik/help/en/) (e.g. 'NOUN >amod ADJ') used by the [SETS](http://depsearch-depsearch.rahtiapp.fi/ds_demo/) online service. Unfortunately, SETS is no longer maintained, but some derivations of it still exist (e.g. https://orodja.cjvt.si/drevesnik/).




