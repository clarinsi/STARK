# STARK: a tool for dependency-tree extraction and analysis
STARK is a highly-customizable open-source tool that extracts various types of syntactic trees from parsed corpora (treebanks) and quantifies them with respect to frequency and other useful statistics, such as the strength of node association and their keyness in comparison to another treebank. It is primarily aimed at processing treebanks based on the [Universal Dependencies](https://universaldependencies.org/) annotation scheme, but it also takes any other dependency treebank in the [CONLL-U](https://universaldependencies.org/format.html) format as input. 

## Installation and execution
Install Python 3 on your system (https://www.python.org/downloads/). 

### Linux users
Install pip and other libraries required by program, by running the following commands in terminal:
```bash
sudo apt install python3-pip
cd <PATH TO PROJECT DIRECTORY>
pip3 install -r requirements.txt
```

Execute extraction by first moving to project directory and executing the script with:
```bash
python3 stark.py 
```

### Windows users
Download pip installation file (https://bootstrap.pypa.io/get-pip.py) and install it by double clicking on it.

Install other libraries necessary for running by going into program directory and double clicking on `install.bat`. If windows defender is preventing execution of this file you might have to unblock that file by `right-clicking on .bat file -> Properties -> General -> Security -> Select Unblock -> Select Apply`.

Execute extraction by running `run.bat` (in case it is blocked repeat the same procedure as for `install.bat`).

### Default settings
By default, running the program as described above extracts trees from the `sample.conllu` file as defined by the settings in the `config.ini` file, i.e. all noun-headed trees occurring with part-of-speech tags as nodes. For more information on how to change the input file, the type of trees to be extracted and all other customizible parameters, see the [Settings](#Settings) section below.

## Output

STARK produces a tab-separated (.tsv) file with a frequency list of all the trees matching the input criteria, as illustrated by the first few lines of the default output below. The description of the tree is given in the first column, while subsequent columns include additional information on individual nodes, the absolute and relative frequencies, the surface node order, and the root. For adding other types of information to the output, such as additional statistics and in-text examples, see Settings below.

|Tree | Node A | Node B | Node C | Abs. Freq. | Rel. Freq. | Order | Nodes | Root Node|
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DET <det NOUN | DET | NOUN |  | 1345 | 10773.0138 | AB | 2 | NOUN| 
| ADP <case DET <det NOUN | ADP | DET | NOUN | 1163 | 9315.2528 | ABC | 3 | NOUN| 
| ADP <case NOUN | ADP | NOUN |  | 1090 | 8730.5465 | AB | 2 | NOUN| 
| PRON <nmod:poss NOUN | PRON | NOUN |  | 487 | 3900.7121 | AB | 2 | NOUN| 
| CCONJ <cc NOUN | CCONJ | NOUN |  | 476 | 3812.6056 | AB | 2 | NOUN| 


## Settings
The type of trees to be extracted can be defined through several parameters in the `config.ini` configuration file.

-	`input`: location of the input file or directory (parsed corpus in .conllu)
-	`output`: location of the output file (extraction results)
-	`internal_saves`: location of the folder with files for optimization during processing
-	`cpu_cores`: number of CPU cores to be used during processing
-	`size`: number of nodes in the tree (integer or range)
-	`complete`: extraction of all possible subtrees or full subtrees only (values *yes* or *no*, default *yes*)
-	`labeled`: extraction of labeled or unlabeled trees (values *yes* or *no*, default *yes*)
-	`fixed`: extraction of trees by taking surface word order into account (values *yes* or *no*, default *yes*)
-	`node_type`: type of nodes under investigation - for multiple use '+' as a separator (values *form*, *lemma*, *upos*, *xpos*, *feats* or *deprel*)
-	`labels`: predefined list of dependency labels allowed in the extracted tree
-	`root`: predefined characteristics of the root node
-	`query`: predefined tree structure based on the modified Turku NLP [query language](http://bionlp.utu.fi/searchexpressions-new.html).
-	`association_measures`: calculate the strength of association between nodes by MI, MI3, t-test, logDice, Dice and simple-LL scores (values *yes* or *no*, default *no*)
-	`frequency_threshold`: minimum frequency of occurrences of the tree in the corpus
-	`max_lines`: maximum number of trees in the output

## Output
The tool returns the resulting list of all relevant trees in the form of a tab-separated `.tsv` file with information on the tree structure, its frequency and other relevant information in relation to specific parameter settings. The tool does not support any data visualization, however, the output structure of the tree is directly transferable to the [Dep_Search](http://bionlp-www.utu.fi/dep_search/) concordancing service giving access to specific examples in many corpora.

## Credits
This program was developed by Luka Krsnik in collaboration with Kaja Dobrovoljc and Marko Robnik Šikonja and with financial support from [CLARIN.SI](https://www.clarin.si/).

<a href="http://www.clarin.si/info/about/"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/CLARIN.png" alt="drawing" height="150"/></a>
<a href="https://www.cjvt.si/en/"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/CJVT.png" alt="drawing" height="150"/></a>
<a href="https://www.fri.uni-lj.si/en/about"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/FRI.png" alt="drawing" height="150"/></a>
<a href="https://www.ff.uni-lj.si/"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/FF.png" alt="drawing" height="150"/></a>
<a href="https://www.arrs.si/"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/ARRS.png" alt="drawing" height="150"/></a>
