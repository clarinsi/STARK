# STARK settings explained

Below is a list of customizable settings that can be used to define the type of trees to be extracted and the associated information in the output. The default values are visible in the [`config.ini`](/config.ini) file and can be modified by following [these instructions](/#changing-the-settings).


|General | Tree specification | Tree restrictions | Statistics | Visualisation | Other |
| --- | --- | --- | --- | --- |  --- | 
| [input](#--input) | [size](#--size) | [labels](#--labels) | [association_measures](#--association_measures) | [grew_match](#--grew_match) | [max_lines](#--max_lines) |
| [output](#--output) | [node_type](#--node_type) | [head](#--head) | [compare](#--compare) | [depsearch](#--depsearch) | [frequency_threshold](#--frequency_threshold) |
|  | [complete](#--complete) | [query](#--query) | |  | [internal_saves](#--internal_saves) |
|  | [labeled](#--labeled) |  |  | | [cpu_cores](#--cpu_cores) |
| | [fixed](#--fixed) |  |  |  | |


## General settings

### `--input`
**Value:** _\<path to the input file or directory\>_

The `--input` parameter defines the location of the input file or directory, i.e. one or more files in the `.conllu` format. The tool is primarily aimed at processing corpora based on the [Universal Dependencies](https://universaldependencies.org/) annotation scheme, but can also be used for any other dependency-parsed corpus complying with the [CONLL-U](https://universaldependencies.org/format.html) format. The only condition is that there is exactly one root node per sentence (named _root_). 

### `--output`
**Value:**_ \<path to the output file\>_

Regardless of the input settings, STARK produces a single tab-separated file (.tsv) as output, the name and the location of which is defined using the `--output` setting. The output file gives a list of all the trees matching the input criteria sorted by descending frequency, as illustrated by the [sample output file](sample/output.tsv).

## Tree specification

### `--size`
**Value:** _\<integer number or range\>_

The obligatory `--size` parameter is defined as the number of tokens (typically words) in the trees under investigation, which can either be specified as an integer number (e.g. _1, 2, 3_ … ) or a range (e.g. _2-5_). Note that trees containing a higher number of tokens (i.e. 10 or more) may necessitate additional processing time.

### `--node_type`
**Values:** _form, lemma, upos, xpos, feats, deprel_

The obligatory `--node_type` parameter specifies which characteristics of the tokens should be considered when extracting and counting the trees: word form (value _form_, e.g. 'went'), lemma (_lemma_, e.g. 'go'), part-of-speech tag (_upos_, e.g. 'VERB'), morphological features (_feats_, e.g. 'Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin'), language-specific tag (_xpos_, e.g. 'VBD'), dependency role (_deprel_, e.g. 'obj') or a combination of them signalled by the '+' operator (e.g. _lemma+upos_). 

For example, while the option _form_ returns trees of the type 'Mary <nsubj went', the option _upos_ returns trees of the type 'PROPN <nsubj VERB'.

### `--complete`
**Values:** _yes, no_

The obligatory `--complete` parameter defines whether STARK, for a given tree size, should only extract complete trees encompassing the head and _all_ its (in)direct dependants (value _yes_), or all possible subtrees spanning from the head, i.e. all possible combinations of the head and its dependants (value _no_). Naturally, the second option places a significantly higher computational demand and should be used with caution.

### `--labeled`
**Values:** _yes, no_

The obligatory `--labeled` parameter specifies whether trees should be differentiated based on the syntactic relations (dependency labels) between the nodes of the tree (value _yes_), or not (value _no_). For example, if the first option differentiates between trees 'NOUN <nsubj VERB' and 'NOUN <obj VERB', the second option considers them as two instances of the same tree, i.e. 'NOUN < VERB'.

### `--fixed`
**Values:** _yes, no_

The obligatory `--fixed` parameter allows the users to specify whether they consider the order of the nodes in the tree, i.e. the surface word order, to be a distinctive feature of the trees (value _yes_) or not (value _no_). For example, if the input treebank contained sentences ‘_John gave the apple to Mary_’ and ‘_John the apple gave to Mary_’ (an odd example in English but typical in languages with free word order), using the _yes_ option would extract the 'gave > apple' and 'apple < gave' as two distinct trees, while the _no_ option would consider them as two instances of the same tree, i.e. 'gave > apple'. 

Note that each of the two options is associated with specific formatting of the trees in the output. When choosing the _fixed = yes_ option, the tree description in the first column reflects the word order of the nodes on the surface (e.g. '(seemingly < easy) < example'). On the other hand, when choosing the _fixed = no_ option, the description of the tree in the first column is order-agnostic, with heads always preceding their dependents, i.e. all the arrows always pointing to the right (e.g. 'example > (easy > seemingly)'. 

The second, order-agnostic description of a tree can also be produced by using the `--depsearch` option (value _yes_), which, in combination with _fixed = yes_, might be useful for users investigating word order variation. 

## Restriction to specific structures
In contrast to the obligatory settings above specifying the criteria for defining the _types_ of trees to be extracted, STARK also allows the users to restrict the extraction procedure to _specific_ trees through the three options presented below.

### `--labels`
**Value:** _\<list of allowed dependency relations\>_

The optional `--labels` parameter defines a list of dependency relations that are allowed to occur in the trees to be extracted (i.e. a whitelist subset of all possible dependency labels) in the form of a list separated by the '|' operator. For example, specifying _labels = obj|iobj|nsubj_ only extracts trees featuring these three relations and ignores all others.

### `--head`
**Value:** _\<list of allowed head characteristics\>_

Similarly, the optional `--head` parameter allows the users to define specific constraints on the head node (i.e. the word that all other words in the (sub-)tree depend on) in the form of attribute-value pairs specifying its lexical or grammatical features. For example, _upos=NOUN_ would only return trees with nouns as heads (nominal phrases) and discard trees spanning from words belonging to other part-of-speech categories. Several restrictions on the head node can be introduced by using the '|' (OR) and '&' (AND) operators, e.g. _upos=NOUN&Case=Acc|upos=NOUN&Case=Nom_ to extract trees governed by nouns in either accusative or nominative case. 

### `--query`
**Value:** _\<pre-defined tree query\>_

Finally, the optional `--query` parameter allows the users to define a specific tree structure to be extracted by using the [DepSearch query language](https://orodja.cjvt.si/drevesnik/help/en/). For example, the query _upos=NOUN >amod (_ >advmod _)_ would return nouns that govern an adjectival modifier modified by an adverbial modifier, e.g. trees of the type '_seemingly easy example_'. Note that the query language requires the attributes to be written in full (e.g. _upos=VERB_, _form=went_, _L=go_).

## Statistics
By default, STARK produces a list of trees with the absolute frequency (raw count) and the relative frequency (normalized count per million tokens) of the trees in the input treebank. In addition, two optional types of statistics can also be computed in the output to help identify compelling syntactic phenomena.

### `--association_measures`
**Values:** _yes, no_

The optional `--association_measures` parameter (value _yes_) produces information on the strength of statistical association between the nodes of the tree by computing several common association scores (MI, MI3 , Dice, logDice, t-score, simple-LL). This is a particularly useful feature for treebank-driven collocation extraction and lexical analysis.

### `--compare`
**Values:** _yes, no_

In addition, STARK can also be used to identify key or statistically significant phenomena in the input treebank by comparing the frequency of the extracted trees to that of another, so-called reference treebank. This is triggered by using the optional `--compare` parameter which takes the name of the second, reference treebank as input (e.g. _sl_ssj-ud-dev.conllu_) to compute the frequencies in both treebanks and compare them using several common keyness scores (LL, BIC, log ratio, odds ratio and %DIFF). This feature is particularly useful for research on language- or genre-specific syntactic phenomena. If a tree occurring in the first treebank is absent from the second treebank (i.e. its frequency is 0), one quadrillionth (0.000000000000000001) is used as a proxy for zero when computing the keyness score to avoid complications arising from division with zero.

## Alternative visualisation and examples
In addition to the [default description of the trees](README.md#description-of-tree-structure) featured in the first column of the output, which is based on the easy-to-read DepSearch query language (e.g. 'ADJ <amod NOUN'), STARK can also produce two alternative ways of describing a tree, which also enable the users to visualisize specific instances of the trees in the related treebank-browsing services.

### `--grew_match`
**Values:** _yes, no_

First, the optional `--grew_match` parameter (value _yes_) produces trees in accordance with the [Grew](https://grew.fr/doc/request/) query language (e.g. 'pattern {A [upos="NOUN"]; B [upos="ADJ"]; A -[amod]-> B }'), which is used by the [Grew-match](https://universal.grew.fr/) online treebank browsing service featuring the latest collections of UD treebanks available in more than 240 languages.

If the name of the input treebank begins with the standard declaration of the language code and the treebank name (e.g. _en_gum-ud..._, _fr_rhapsodie-ud..._, _sl_ssj-ud..._), the _grew_match = yes_ option will also produce direct URL links to the instances of the tree in the latest version of the given input treebank, e.g. [this URL](http://universal.grew.fr/?corpus=UD_English-GUM&request=pattern%20%7BB%20%5Bupos%3DNOUN%5D%3B%20A%20%5Bupos%3DADJ%5D%3B%20B%20-%5Bamod%5D-%3E%20A%3B%20B%20%3E%3E%20A%7D) for the 'ADJ <amod NOUN' case at hand.

### `--depsearch`
**Values:** _yes, no_

Second, the optional `--depsearch` parameter (value _yes_) produces trees in accordance with the [DepSearch query language](https://orodja.cjvt.si/drevesnik/help/en/) (e.g. 'NOUN >amod ADJ'), which is used by the [SETS](http://depsearch-depsearch.rahtiapp.fi/ds_demo/) online treebank-browsing service. Unfortunately, SETS is no longer maintained, but some derivations of it still exist, such as [Drevesnik](https://orodja.cjvt.si/drevesnik/).


## Other settings

### `--frequency_threshold`
**Value:** _\<minimum number of tree occurrances in the input treebank\>_

To limit the number of trees in the output file, the optional `--frequency_threshold` parameter can be used to limit the extraction to trees occurring above a given threshold by specifying the minimal absolute frequency of the tree in the treebank (e.g. _5_ to limit the search to trees occurring 5 or more times). 

### `--max_lines`
**Value:** _\<maximum number of lines in the output file\>_

Similarly, the optional `--max_lines` parameter defines the maximum number of trees (lines) in the output file, which gives a frequency-ranked list of trees. For example, value _100_ returns only the top-100 most frequent trees matching the input criteria.

### `--internal_saves`
**Value:** _\<path to folder for internal storage\>_

The optional `--internal_saves` parameter speeds up performance for users repeating several different queries on the same treebank, as it avoids repeating same parts of the execution twice. To test it, simply uncomment the parameter in the `config.ini` file or provide a different path for the internal data storage.

### `--cpu_cores`
**Value:** _\<integer number\>_

By default, STARK uses all available processors except one. The optional `--cpu_core` parameter allows the users to define a specific number of processors to be used in the process, for example to boost the tool's performance by running it on all available CPU cores.




