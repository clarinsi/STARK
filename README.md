# STARK: a tool for statistical analysis of dependency-parsed corpora
STARK is a python-based command-line tool for extraction of dependency trees from parsed corpora based on various user-defined criteria. It is primarily aimed at processing corpora based on the [Universal Dependencies](https://universaldependencies.org/) annotation scheme, but it also takes any other corpus in the [CONLL-U](https://universaldependencies.org/format.html) format as input. 

## Windows installation and execution
### Installation
Install Python 3 on your system (https://www.python.org/downloads/).

Download pip installation file (https://bootstrap.pypa.io/get-pip.py) and install it by double clicking on it.

Install other libraries necessary for running by going into program directory and double clicking on `install.bat`. If windows defender is preventing execution of this file you might have to unblock that file by `right-clicking on .bat file -> Properties -> General -> Security -> Select Unblock -> Select Apply`.

### Execution
Set up search parameters in `.ini` file.

Execute extraction by running `run.bat` (in case it is blocked repeat the same procedure as for `install.bat`).
Optionally modify run.bat by pointing it to another .ini file. This can be done by editing run.bat file (changing parameter --config_file).


## Linux installation and execution
### Installation
Install Python 3 on your system (https://www.python.org/downloads/). 

Install pip and other libraries required by program, by running the following commands in terminal:
```bash
sudo apt install python3-pip
cd <PATH TO PROJECT DIRECTORY>
pip3 install -r requirements.txt
```

### Execution
Set up search parameters in `.ini` file.

Execute extraction by first moving to project directory with:
```bash
cd <PATH TO PROJECT DIRECTORY>
```

And later executing script with:
```bash
python3 dependency-parsetree.py --config_file=<PATH TO .ini file>
```

Example:
```bash
python3 dependency-parsetree.py --config_file=config.ini
```

## Parameter settings
The type of trees to be extracted can be defined through several parameters in the `config.ini` configuration file.

-	`input`: location of the input file or directory (parsed corpus in .conllu)
-	`output`: location of the output file (extraction results)
-	`internal_saves`: location of the folder with files for optimization during processing
-	`cpu_cores`: number of CPU cores to be used during processing
-	`tree_size`: number of nodes in the tree (integer or range)
-	`tree_type`: extraction of all possible subtrees or full subtrees only (values *all* or *complete*)
-	`dependency_type`: extraction of labeled or unlabeled trees (values *labeled* or *unlabeled*)
-	`node_order`: extraction of trees by taking surface word order into account (values *free* or *fixed*)
-	`node_type`: type of nodes under investigation - for multiple use '+' as a separator (values *form*, *lemma*, *upos*, *xpos*, *feats* or *deprel*)
-	`label_whitelist`: predefined list of dependency labels allowed in the extracted tree
-	`root_whitelist`: predefined characteristics of the root node
-	`query`: predefined tree structure based on the modified Turku NLP [query language](http://bionlp.utu.fi/searchexpressions-new.html).  
-	`print_root`: print root node information in the output file (values *yes* or *no*)
-	`nodes_number`: print the number of nodes in the tree in the output file (values *yes* or *no*)
-	`association_measures`: calculate the strength of association between nodes by MI, MI3, t-test, logDice, Dice and simple-LL scores (values *yes* or *no*)
-	`frequency_threshold`: minimum frequency of occurrences of the tree in the corpus
-	`lines_threshold`: maximum number of trees in the output

## Output
The tool returns the resulting list of all relevant trees in the form of a tab-separated `.tsv` file with information on the tree structure, its frequency and other relevant information in relation to specific parameter settings. The tool does not support any data visualization, however, the output structure of the tree is directly transferable to the [Dep_Search](http://bionlp-www.utu.fi/dep_search/) concordancing service giving access to specific examples in many corpora.

## Credits
This program was developed by Luka Krsnik in collaboration with Kaja Dobrovoljc and Marko Robnik Šikonja and with financial support from [CLARIN.SI](https://www.clarin.si/).

<a href="http://www.clarin.si/info/about/"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/CLARIN.png" alt="drawing" height="150"/></a>
<a href="https://www.cjvt.si/en/"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/CJVT.png" alt="drawing" height="150"/></a>
<a href="https://www.fri.uni-lj.si/en/about"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/FRI.png" alt="drawing" height="150"/></a>
<a href="https://www.ff.uni-lj.si/"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/FF.png" alt="drawing" height="150"/></a>
<a href="https://www.arrs.si/"><img src="https://raw.githubusercontent.com/clarinsi/STARK/master/logos/ARRS.png" alt="drawing" height="150"/></a>
