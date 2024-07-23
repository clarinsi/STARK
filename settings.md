# STARK settings explained

Below is a list of customizable settings that can be used to define the type of trees to be extracted and the associated information in the output. The default values are visible in the [`config.ini`](/config.ini) file and can be modified by following [these instructions](/#changing-the-settings).


|General | Tree specification | Tree restrictions | Statistics | Visualisation | Threshold |
| --- | --- | --- | --- | --- |  --- | 
| [input](#--input) | [node_type](#--node_type) | [size](#--size) | [association_measures](#--association_measures) | [example](#--example) | [max_lines](#--max_lines) |
| [output](#--output) | [labeled](#--labeled) | [head](#--head) | [compare](#--compare) | [grew_match](#--grew_match) | [frequency_threshold](#--frequency_threshold) |
|  | [label_subtypes](#--label_subtypes) | [ignored_labels](#--ignored_labels)| | [depsearch](#--depsearch) | |
|  | [fixed](#--fixed) | [allowed_labels](#--allowed_labels)  |  |  |  |
|  |  |  [query](#--query)|  |  |  |




For details on the settings pertaining to the tool performance, testing and rare use cases see [advanced settings](/advanced.md).


## General settings

### `--input`
**Value:** _\<path to the input file or directory\>_

The `--input` parameter defines the location of the input file or directory, i.e. one or more files in the `.conllu` format. The tool is primarily aimed at processing corpora based on the [Universal Dependencies](https://universaldependencies.org/) annotation scheme, but can also be used for any other dependency-parsed corpus complying with the [CONLL-U](https://universaldependencies.org/format.html) format, regardless of the tagsets used. The only condition is that there is at least one root node per sentence named _root_ (regardless of the casing).

### `--output`
**Value:** _\<path to the output file\>_

STARK produces a single tab-separated file (.tsv) as output, the name and the location of which is defined using the `--output` setting. The output file gives a list of all the trees matching the input criteria sorted by descending frequency, as illustrated by the [sample output file here](sample/output.tsv).


## Tree specification

### `--node_type`
**Values:** _form, lemma, upos, xpos, feats, deprel_

The `--node_type` parameter specifies which characteristics of the tokens should be considered when extracting and counting the trees: word form (value _form_, e.g. 'went'), lemma (_lemma_, e.g. 'go'), part-of-speech tag (_upos_, e.g. 'VERB'), morphological features (_feats_, e.g. 'Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin'), language-specific tag (_xpos_, e.g. 'VBD'), dependency role (_deprel_, e.g. 'obj'). You can also combine these values using the '+' operator (e.g. _lemma+upos_). If you do not want to differentiate your trees based on their nodes, simply comment the '--node_type' parameter to get trees with underscores as nodes.

For example, specifying the option _form_ returns trees of the type 'Mary <nsubj went', while specifying the option _upos_ returns trees of the type 'PROPN <nsubj VERB'. If this parameter is not specified, the trees are returned in the form '_ nsubj _'.

### `--labeled`
**Values:** _yes, no_

The obligatory `--labeled` parameter specifies whether trees should be differentiated based on the syntactic relations (dependency labels) between the nodes of the tree (value _yes_), or not (value _no_). 

For example, if the first option differentiates between trees 'NOUN <nsubj VERB' and 'NOUN <obj VERB', the second option considers them as two instances of the same tree, i.e. 'NOUN < VERB'.

### `--label_subtypes`
**Values:** _yes, no_

The obligatory `--label_subtypes` parameter specifies whether (labeled) trees should be differentiated based on label extensions, i.e. colon-marked relation sub-types (value _yes_), or not (value _no_). 

For example, if specifying the option _yes_ differentiates between trees 'NOUN <nsubj:pass VERB' and 'NOUN <nsubj VERB', specifying the option _no_ considers them as two instances of the same tree, i.e. 'NOUN <nsubj VERB'.

### `--fixed`
**Values:** _yes, no_

The obligatory `--fixed` parameter allows the users to specify whether they consider the order of the nodes in the tree, i.e. the surface word order, to be a distinctive feature of the trees (value _yes_) or not (value _no_). 

For example, if the input treebank contained sentences ‘_John gave the apple to Mary_’ and ‘_John the apple gave to Mary_’ (an odd example in English but common in languages with free word order), using the _yes_ option would extract the 'gave > apple' and 'apple < gave' as two distinct trees, while the _no_ option would consider them as two instances of the same tree, i.e. 'gave > apple'. 

Note that each of the two options is associated with specific formatting of the trees in the output. When choosing the _fixed = yes_ option, the tree description in the first column reflects the word order of the nodes on the surface (e.g. '(seemingly < easy) < example'). On the other hand, when choosing the _fixed = no_ option, the description of the tree in the first column is order-agnostic, with heads always preceding their dependents, i.e. all the arrows always pointing to the right (e.g. 'example > (easy > seemingly)'. 

The second, order-agnostic description of a tree can also be produced by using the `--depsearch` option (value _yes_), which--in combination with _fixed = yes_--might be useful for users investigating word order variation. 


## Restriction to specific structures
In contrast to the obligatory settings above specifying the criteria for defining the _types_ of trees to be extracted, STARK also allows the users to restrict the extraction procedure to _specific_ trees through the five options presented below.

### `--size`
**Value:** _\<integer number or range\>_

The obligatory `--size` parameter allows the users to define the size of the trees to appear in the output file, i.e. the number of tokens (typically words) in the trees under investigation, which can either be specified as an integer number (e.g. _1, 2, 3_ … ) or a range (e.g. _2-15_). If you want to retrieve all possible trees regardless of size, set the maximum value to a very large number, e.g. _1-10000_.

### `--head`
**Value:** _\<list of allowed head characteristics\>_

The optional `--head` parameter allows the users to define specific constraints on the head node (i.e. the word that all other words in the (sub-)tree depend on) in the form of attribute-value pairs specifying its lexical or grammatical features. 

For example, _upos=NOUN_ would only return trees with nouns as heads (nominal phrases) and discard trees spanning from words belonging to other part-of-speech categories. Several restrictions on the head node can be introduced by using the '|' (OR),  '&' (AND) and '!' (NOT) operators, e.g. specifying _lemma=chair&upos=NOUN|lemma=bank&upos=VERB_ to extract trees spanning from the verb or noun 'chair'. 

### `--ignored_labels`
**Value:** _\<list of dependency relations to be ignored\>_

The optional `--ignored_labels` parameter defines a list of dependency relations that are to be ignored when matching the trees and thus not displayed in the results file. 

For example, specifying _ignored_labels = punct_ produces a list of matched trees that do not include the _punct_ relation (even if it is present in the actual tree). In addition to ignoring a certain type of relations, such as punctuation or other clause-peripheral phenomena, this is a particularly useful feature for users interested in a limited set of relations only, such as core predicate arguments. Such users would then use this parameter as a negative filter by specifying all relations except those pertaining to the core predicate arguments (e.g. _nsubj, obj_). In contrast to the `--allowed_labels` parameter below, this parameter does not exclude trees containing a given relation, but only ignores them when they occur in a tree. Two or more relations specified should be separated by the '|' operator.

### `--allowed_labels`
**Value:** _\<whitelist of allowed dependency relations\>_

The optional `--allowed_labels` parameter defines a list of dependency relations that are allowed to occur in the trees to be extracted (i.e. a whitelist subset of all possible dependency labels) in the form of a list separated by the '|' operator. 

For example, specifying _allowed_labels = obj|iobj|nsubj_ extracts trees featuring only these three relations (and no other) and ignores all others. In contrast to the `--ignored_labels` parameter above, the presence of any other label in the tree automatically excludes such tree from being matched and counted.  

### `--query`
**Value:** _\<pre-defined tree query\>_

Finally, the optional `--query` parameter allows the users to define a specific tree structure to be extracted by using the [dep_search query language](https://orodja.cjvt.si/drevesnik/help/en/). 

For example, the query _upos=NOUN >amod (\_ >advmod \_)_ would return nouns that govern an adjectival modifier modified by an adverbial modifier, e.g. trees of the type '_seemingly easy example_'. The query language requires the attributes to be written in full (e.g. _upos=VERB_, _form=went_, _L=go_) and also supports using the '|' (OR),  '&' (AND), and '!' (NOT) operators, with some minor deviations. 

When `--query` is specified, the output takes into account [tree specification settings](#tree-specification), such as `--node_type`, but ignores all other [tree restriction settings](#restriction-to-specific-structure), such as `--size`.

## Statistics
By default, STARK produces a list of trees with the absolute frequency (raw count) and the relative frequency (normalized count per million tokens) of the trees in the input treebank. In addition, two optional types of statistics can also be computed in the output to help identify compelling syntactic phenomena.

### `--association_measures`
**Values:** _yes, no_

The optional `--association_measures` parameter (value _yes_) produces information on the strength of statistical association between the nodes of the tree by computing several common association scores (MI, MI3 , Dice, logDice, t-score, simple-LL). This is a particularly useful feature for treebank-driven collocation extraction and lexical analysis.

### `--compare`
**Values:** _yes, no_

In addition, STARK can also be used to identify key or statistically significant phenomena in the input treebank by comparing the frequency of the extracted trees to that of another, so-called reference treebank. This is triggered by using the optional `--compare` parameter which takes the name of the second, reference treebank as input (e.g. _sl_ssj-ud-dev.conllu_) to compute the frequencies in both treebanks and compare them using the simple ratio comparison and several common keyness scores (LL, BIC, log ratio, odds ratio and %DIFF). This feature is particularly useful for research on language- or genre-specific syntactic phenomena. 

If a tree occurring in the first treebank is absent from the second treebank (i.e. its frequency is 0), one quadrillionth (0.000000000000000001) is used as a proxy for zero when computing the keyness scores to avoid complications arising from division with zero. When calculating the simple ratio, NaN value is given.

## Alternative visualisation and examples

In addition to the [default description of the trees](README.md#description-of-tree-structure) featured in the first column of the output, which is based on the easy-to-read DepSearch query language (e.g. 'ADJ <amod NOUN'), STARK can also produce two alternative ways of describing a tree, which also enable the users to visualisize specific instances of the trees in the related treebank-browsing services.

### `--grew_match`
**Values:** _yes, no_

First, the optional `--grew_match` parameter (value _yes_) produces trees in accordance with the [Grew](https://grew.fr/doc/request/) query language (e.g. 'pattern {A [upos="NOUN"]; B [upos="ADJ"]; A -[amod]-> B }'), which is used by the [Grew-match](https://universal.grew.fr/) online treebank browsing service featuring the latest collections of UD treebanks available in more than 240 languages.

If the name of the input treebank begins with the standard declaration of the language code and the treebank name (e.g. _en_gum-ud..._, _fr_rhapsodie-ud..._, _sl_ssj-ud..._), the _grew_match = yes_ option will also produce direct URL links to the instances of the tree in the latest version of the given input treebank, e.g. [this URL](http://universal.grew.fr/?corpus=UD_English-GUM&request=pattern%20%7BB%20%5Bupos%3DNOUN%5D%3B%20A%20%5Bupos%3DADJ%5D%3B%20B%20-%5Bamod%5D-%3E%20A%3B%20B%20%3E%3E%20A%7D) for the 'ADJ <amod NOUN' case at hand.

### `--depsearch`
**Values:** _yes, no_

Second, the optional `--depsearch` parameter (value _yes_) produces trees in accordance with the [DepSearch query language](https://orodja.cjvt.si/drevesnik/help/en/) (e.g. 'NOUN >amod ADJ'), which is used by the [SETS](http://depsearch-depsearch.rahtiapp.fi/ds_demo/) online treebank-browsing service. Unfortunately, SETS is no longer maintained, but some derivations of it still exist, such as [Drevesnik](https://orodja.cjvt.si/drevesnik/).

### `--example`
**Values:** _yes, no_

Additionaly, using the `--example` parameter (value _yes_) produces an additional column with one random sentence containing the tree, in which the nodes of the tree are explicitely marked, e.g. a sentence _We went to see \[the\]<sub>A</sub> \[new\]<sub>B</sub> \[trains\]<sub>C</sub>._, for a tree of the type 'DET < ADJ < NOUN'.

## Threshold settings

### `--frequency_threshold`
**Value:** _\<minimum number of tree occurrances in the input treebank\>_

To limit the number of trees in the output file, the optional `--frequency_threshold` parameter can be used to limit the extraction to trees occurring above a given threshold by specifying the minimal absolute frequency of the tree in the treebank (e.g. _5_ to limit the search to trees occurring 5 or more times). 

### `--max_lines`
**Value:** _\<maximum number of lines in the output file\>_

Similarly, the optional `--max_lines` parameter defines the maximum number of trees (lines) in the output file, which gives a frequency-ranked list of trees. For example, value _100_ returns only the top-100 most frequent trees matching the input criteria.




