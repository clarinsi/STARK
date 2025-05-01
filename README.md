# STARK: A Tool for Dependency (Sub)Tree Extraction and Comparison

**A bottom-up tool for discovering syntactic patterns in parsed corpora — no predefined queries needed.**


![STARK_demonstration_loop](https://github.com/user-attachments/assets/6e6947bd-0db0-401f-bc69-59d9fc960e14)


STARK is a highly customizable tool designed for extracting different types of syntactic structures (trees and subtrees) from parsed corpora (treebanks). It quantifies these structures with respect to frequency and provides other useful corpus-linguistic statistics, such as the strength of association between the nodes of a tree or its statistical significance in comparison to another treebank. 

STARK is primarily aimed at processing treebanks based on the [Universal Dependencies](https://universaldependencies.org/) annotation scheme, but it also takes any other dependency treebank in the CONLL-U format as input. 

For an online demonstration of the tool (with a slightly reduced set of features), please visit [https://orodja.cjvt.si/stark/](https://orodja.cjvt.si/stark/).


## Installation and execution
Install Python 3 on your system https://www.python.org/downloads/.

### Linux users
Install pip and other libraries required by the program, by running the following commands in the terminal:
```bash
sudo apt install python3-pip
pip3 install stark-trees
```

Execute extraction by first moving to the project directory and executing the script with:
```bash
stark --config_file <PATH TO my-settings.ini FILE>
```

### Windows users
Download pip installation file (https://bootstrap.pypa.io/get-pip.py) and install it by double clicking on it.

Install other libraries necessary for running by going into program directory and double clicking on `install.bat`. If windows defender is preventing execution of this file you might have to unblock that file by `right-clicking on .bat file -> Properties -> General -> Security -> Select Unblock -> Select Apply`.

Execute extraction by running `run.bat` (in case it is blocked repeat the same procedure as for `install.bat`).

## Changing the settings
By default, running the program as described above extracts trees from the sample `en_ewt-ud-dev.conllu` file (taken from the [English EWT](https://universaldependencies.org/treebanks/en_ewt/index.html) UD v2.14 treebank) as defined by the parameter settings in the default [`config.ini`](config.ini) file. To change the [settings](#list-of-main-settings), you can modify the `config.ini` file directly or create your own configuration (`.ini`) file, which is then passed as an argument when running the program in the terminal (example below) or specified in the `run.bat` file. 

```bash
python3 stark.py --config_file my-settings.ini
```
Alternatively, you can change a specific setting by introducing it as a command line argument directly, which overrides the default setting specified in the `config.ini` configuration file. In the example below, the tool extracts verb-headed trees with lemmas as nodes from a treebank named `my-treebank.conllu`, while all other options remain the same as in the default `config.ini` configuration file.

```bash
python3 stark.py --input my-treebank.conllu --node_type lemma --head upos=VERB
```

## List of main settings
The types of trees to be extracted and the associated output information can be defined through the main parameters listed below and [described in more detail here](settings.md).

General settings:
-	`input`: location of the input file or directory (parsed corpus in _.conllu_)
-	`output`: location of the output file (list of trees in _.tsv_)

Tree specification:
- `node_type`: node characteristic under investigation (*form*, *lemma*, *upos*, *xpos*, *feats*, *deprel* or none)
-	`labeled`: extraction of labeled or unlabeled trees (values *yes* or *no*)
-	`fixed`: differentiating trees by surface word order (values *yes* or *no*)

Tree restrictions:
-	`size`: number of nodes in the tree (integer or range, e.g. _2-10_)
-	`head`: predefined characteristics of the head node (e.g. _upos=NOUN_)
-	`ignored_labels`: predefined list of dependency labels to be ignored when retrieving the trees (e.g. _punct_)
-	`query`: predefined tree structure based on the DepSearch query language (e.g. _upos=VERB >obl upos=NOUN_).

Statistics: 
-	`association_measures`: calculates the strength of association between nodes by MI, MI3, t-test, logDice, Dice and simple-LL scores (values *yes* or *no*)
- `compare`: calculates the keyness of a tree in comparison to another treebank by LL, BIC, log ratio, odds ratio and %DIFF scores (reference treebank in _.conllu_)

Additional visualization:
- `example`: prints a random sentence containing the tree
- `grew_match`: provides links to examples in [Grew-match](https://universal.grew.fr/) and describes the tree structure using the grew query language

For a detailed explanation of these and many other settings, see the [settings documentation here](settings.md).

## Output

[<img src="https://github.com/user-attachments/assets/cf2516f3-3b91-4099-98e2-dd648b43ee8b" alt="Input-output flow">](https://orodja.cjvt.si/stark/)

STARK produces a tab-separated (.tsv) file with a list of all the trees matching the input criteria sorted by descending frequency, as illustrated by the first few lines of the default [sample output](/sample/output.tsv) below, which show the 5-most frequent trees occurring in the sample `en_ewt-ud-dev.conllu` treebank.

The description of the tree is given in the first column, while subsequent columns additional information on the absolute and relative frequencies, the surface node order, the number of the nodes in the tree and the head node. For adding other types of information to the output, such as other useful statistics, examples and links to visualized trees, see the list of settings above or the [detailed settings documentation here](settings.md).

|Tree | Abs-Freq | Rel-Freq | Order | N | Head
| --- | --- | --- | --- | --- | --- | 
| DET <det NOUN | 320 | 12644.6 | AB | 2 | NOUN
| ADP <case DET <det NOUN | 183 | 7276.6 | ABC | 3 | NOUN
| ADP <case PROPN | 175 | 6958.5 | AB | 2 | PROPN
| ADP <case NOUN | 163 | 6481.4 | AB | 2 | NOUN
| ADJ <amod NOUN | 117 | 4652.3 | AB | 2 | NOUN

### Description of tree structure
The description of the trees given in the first column of the output is based on the [dep_search](https://fginter.github.io/dep_search/) query language (archived [here](https://orodja.cjvt.si/drevesnik/help/en/)), which is simple to learn and easy to read:
- Dependencies are expressed using < and > operators, which mimic the "arrows" in the dependency graph.
  - A < B means that token A is governed by token B, e.g. _rainy < morning_
  - A > B means that token A governs token B, e.g. _read > newspapers_
- Dependency labels are specified right after the dependency operator
  - A <amod B means that token A is the adjectival modifier of token B, e.g. _rainy <amod morning_
  - A >obj B means that token B is the direct object of token A, e.g. _read >obj newspapers_
- Priority is marked using parentheses:
  -   A > B > C means that A governs both B and C in parallel, e.g. _read > newspapers > people_ for 'people read newspapers'
  -   A > (B > C) means that A governs B which, in turn, governs C, e.g. _read > (newspapers > interesting)_ for 'read interesting newspapers'
  
## Acknowledgment
This tool was developed by Luka Krsnik in collaboration with Kaja Dobrovoljc and Marko Robnik Šikonja. Financial and infrastructural support was provided by Slovenian Research and Innovation Agency, CLARIN.SI and CJVT UL as part of the research projects [SPOT: A Treebank-Driven Approach to the Study of Spoken Slovenian](https://spot.ff.uni-lj.si/) (Z6-4617) and _Language Resources and Technologies for Slovene_ (P6-0411), as well as through the 2019 and 2024 _CLARIN.SI Resource and Service Development_ grants.

<p align="center">
<a href="http://www.clarin.si/info/about/"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/CLARIN.png" alt="drawing" height="90"/></a>
<a href="https://www.aris-rs.si/"><img src="https://pbs.twimg.com/profile_images/1696069698289332224/tB-Z74Tn_400x400.jpg" alt="drawing" height="110"/></a>
<a href="https://www.cjvt.si/en/"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/CJVT.png" alt="drawing" height="70"/></a>
</p>

