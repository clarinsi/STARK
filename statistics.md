# Statistics explained

By default, STARK produces a list of trees with the **absolute frequency** (raw count) and the **relative frequency** (normalized count per million tokens) of the trees in the input treebank. In addition, three optional types of statistics can also be computed in the output to help identify compelling syntactic phenomena: **association measures**, **keyness measures** and **complexity measures**.

## Association measures

In corpus linguistics, association measures (also known as collocation scores) are statistical tools used to evaluate the strength of association between words in a corpus. They compare the observed frequency of a word pair (or n-gram) with its expected frequency under the assumption of independence. Below is the list of association measures used in STARK, where trees serve as the sequences of interest and nodes as their constituent elements.

### Input data
| **Notation**               | **Meaning**                                                                                                   | **Example**                                                                 |
|------------------------|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **$c(w_1 \ldots w_n)$** | Absolute frequency of the tree.                                      | Frequency of `read > newspapers` tree in the treebank.                               |
| **$c(w_i)$**            | Frequency of the $i$-th node (word) in the tree (where $i = 1, 2, \ldots, n$).                                 | - $c(w_1)$ = frequency of `read` (first node).<br>- $c(w_2)$ = frequency of `newspapers` (second node). |
| **$N$**                 | Total number of nodes (words) in the treebank.                                                             | If the treebank has 1,000,000 words, $N = 1,000,000$.                        |
| **$n$**                 | Length of the tree (number of nodes in the tree).                                                       | For a two-word tree (`read > newspapers`), $n = 2$.                                            |

### Expected Frequency

The expected frequency of the tree is computed as:

$$
E(w_1 \ldots w_n) \approx \frac{c{(w_1) \ldots c(w_n)}}{N^{(n-1)}}
$$


### Collocation Measures


| **Measure**                          | **Equation**                                                                                                                                                                   |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **[Mutual Information (MI)](https://wordbanks.harpercollins.co.uk/other_doc/statistics.html)**         | $\displaystyle \text{MI} = \log_2\left(\frac{c(w_1 \ldots w_n)}{E(w_1 \ldots w_n)}\right)$                                                                                           |
| **MI³**                           | $\displaystyle \text{MI}^3 = \log_2\left(\frac{c(w_1 \ldots w_n)^3}{E(w_1 \ldots w_n)}\right)$                                                                                         |
| **Dice Coefficient**                | $\displaystyle \text{Dice} = \frac{n \times c(w_1 \ldots w_n)}{\sum_{i=1}^{n} c(w_i)}$                                                                                                   |
| **[log-Dice](https://www.sketchengine.eu/glossary/logdice/)**                        | $\displaystyle \text{logDice} = 14 + \log_2\left(\text{Dice}\right)$                                                                                                            |
| **[t-score](https://wordbanks.harpercollins.co.uk/other_doc/statistics.html)**                          | $\displaystyle \text{t-score} = \frac{c(w_1 \ldots w_n) - E(w_1 \ldots w_n)}{\sqrt{c(w_1 \ldots w_n)}}$                                                                                          |
| **Simple Log-Likelihood (LL)**      | $\text{LL} = 2 \times \left(c(w_1 \ldots w_n) \log_{10}\left(\frac{c(w_1 \ldots w_n)}{E(w_1 \ldots w_n)}\right) - \Bigl(c(w_1 \ldots w_n) - E(w_1 \ldots w_n)\Bigr)\right)$  |

## Keyness measures
In corpus linguistics, keyness measures are statistical tools that compare the frequency of words in a target corpus with their frequency in a reference corpus to highlight distinctive vocabulary. Below is the list of keyness measures used in STARK, where trees serve as the phenomena of interest rather than individual words.

### Input data

| **Notation**              | **Meaning**                                                                                     | **Example**                                                                 |
|-----------------------|-------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **$a = \text{RFC}_1$** | Absolute (raw) frequency of the tree in **Treebank 1**.                                         | If `read > newspapers` appears 50 times in Treebank 1, then $a = 50$.                     |
| **$b = \text{RFC}_2$** | Absolute (raw) frequency of the tree in **Treebank 2**. | If `read > newspapers` appears 30 times in Treebank 2, then $b = 30$. |
| **$c = \text{C}_1$**   | Total number of **tokens** (words) in **Treebank 1**.                                             | If Treebank 1 has 1,000,000 words, then $c = 1,000,000$.                       |
| **$d = \text{C}_2$**   | Total number of **tokens** (words) in **Treebank 2**.                                             | If Treebank 2 has 800,000 words, then $d = 800,000$.                           |


### Normalized Frequencies
Normalized frequencies are calculated by dividing the frequency by the total treebank size:

$$ \text{NFC}_1 = \frac{a}{c} = \frac{\text{RFC}_1}{\text{C}_1}, \quad \text{NFC}_2 = \frac{b}{d} = \frac{\text{RFC}_2}{\text{C}_2} $$

### Expected Frequencies

Expected frequencies are computed as:

$$ E_1 = \frac{c (a + b)}{c + d}, \quad E_2 = \frac{d (a + b)}{c + d} $$

## Keyness measures

| **Measure**         | **Equation**                                                                                                                                               |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| $\text{LL}$        | $\displaystyle \text{LL} = 2 \times \left( a \log\left(\frac{a}{E_1}\right) + b \log\left(\frac{b}{E_2}\right) \right)$                                                                |
| $\text{BIC}$       | $\displaystyle \text{BIC} = \text{LL} - \log(c + d)$                                                                                                                                   |
| $\text{Log Ratio}$ | $\displaystyle \text{Log Ratio} = \log_2 \left(\frac{\text{NFC}_1}{\text{NFC}_2}\right)$                                                                                                      |
| $\text{OR}$        | $\displaystyle \text{OR} = \frac{\text{RFC}_1/(\text{C}_1 - \text{RFC}_1)}{\text{RFC}_2/(\text{C}_2 - \text{RFC}_2)}$                                                                                                                   |
| $\\%\text{DIFF}$    | $\displaystyle \text{\\%DIFF} = \frac{(\text{NFC}_1 - \text{NFC}_2) \times 100}{\text{NFC}_2}$                                                                                              |

## Complexity measures
Syntactic complexity measures describe the structure of a tree, e.g. how deeply it is nested, how far apart related words are, and how many clauses it contains. They are enabled with `complexity_measures = yes` (basic measures) or `complexity_measures = extended` (all measures). Each measure is computed for every occurrence of a tree and then averaged over all its occurrences in the treebank; values for individual occurrences are given in the `detailed_results_file`, if specified.

Note that all measures describe the **extracted tree**, not the whole sentence it occurs in. For example, the tree `reads > newspapers` extracted from *Mary reads old newspapers.* contains only two nodes and one dependency, regardless of the rest of the sentence. The measures correspond to sentence-level values only when the entire sentence tree is extracted (e.g. with `complete = yes` and a sufficiently large `size`).

### Input data
| **Notation**   | **Meaning**                                                                                                          | **Example** (tree `reads >obj newspapers` in *Mary reads old newspapers.*)    |
|----------------|----------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| **$m$**        | Number of dependencies (arcs) in the tree, excluding punctuation (`punct`).                                         | $m = 1$ (`reads > newspapers`).                                               |
| **$d_i$**      | Dependency distance of the $i$-th arc: the absolute difference between the positions of the head and the dependent. | - In the sentence: $d_1 = \lvert 2 - 4 \rvert = 2$.<br>- In the tree: $d_1 = \lvert 1 - 2 \rvert = 1$. |
| **$r$**        | Position of the root node of the tree.                                                                               | - In the sentence: $r = 2$ (`reads`).<br>- In the tree: $r = 1$.             |

Positions are counted in two ways: **in the sentence** (the original token positions) and **in the tree** (the nodes of the extracted tree renumbered 1, 2, 3, … in their surface order, ignoring the words that are not part of the tree). The first reflects how the tree is realized in the actual sentences, while the second depends only on the shape and word order of the tree itself. Punctuation arcs are not counted as dependencies, but punctuation nodes included in the tree still occupy a position.

### Measures

| **Measure**          | **Mode**     | **Definition**                                                                                                                                                         |
|----------------------|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Max depth**        | yes/extended | Number of levels in the tree, where the root is level 1 (e.g. `reads > newspapers` has depth 2, `reads > newspapers > old` has depth 3).                              |
| **MDD**              | yes/extended | Mean dependency distance with positions counted **in the tree**: $\displaystyle \text{MDD} = \frac{1}{m}\sum_{i=1}^{m} d_i$                                          |
| **MDD-mean**         | yes/extended | Mean dependency distance with positions counted **in the sentence** (same equation as above).                                                                          |
| **NDD**              | extended     | Normalized dependency distance, adapted from Jiang & Liu (2015), with positions counted **in the tree**: $\displaystyle \text{NDD} = \left\lvert \ln\left(\frac{\text{MDD}}{\sqrt{r \times m}}\right) \right\rvert$ |
| **NDD-mean**         | extended     | Normalized dependency distance with positions counted **in the sentence** (same equation as above, using MDD-mean).                                                    |
| **N clauses**        | extended     | Number of clauses: 1 (the root) + the number of verbal dependents attached with `csubj`, `ccomp`, `xcomp`, `advcl`, `acl`, `conj` or `parataxis`.                    |
| **N T-units**        | extended     | Number of T-units (main clauses with their dependent clauses): 1 (the root) + the number of verbal dependents attached with `conj` or `parataxis`.                    |
| **Clauses/T-unit**   | extended     | Average number of clauses per T-unit: $\displaystyle \frac{\text{N clauses}}{\text{N T-units}}$                                                                       |

A dependent is considered verbal if its UPOS tag is `VERB` or if it has a copula (`cop`) dependent within the extracted tree.

The extended measures **NDD**, **NDD-mean**, **N clauses**, **N T-units** and **Clauses/T-unit** are only computed for occurrences where the root of the tree is also the root of the sentence (i.e. has the `root` relation), and are averaged over these occurrences only. If a tree never occurs in this position, these values are given as `n/a`.

Example values (from STARK output) for trees extracted from *Mary reads old newspapers.*:

| **Tree**                                     | **Max depth** | **MDD** | **MDD-mean** | **NDD** | **NDD-mean** | **N clauses** | **N T-units** |
|----------------------------------------------|---------------|---------|--------------|---------|--------------|---------------|---------------|
| `reads >obj newspapers`                      | 2             | 1.00    | 2.00         | 0.00    | 0.35         | 1.00          | 1.00          |
| `Mary <nsubj reads >obj (old <amod newspapers)` | 3          | 1.33    | 1.33         | 0.61    | 0.61         | 1.00          | 1.00          |
| `old <amod newspapers`                       | 2             | 1.00    | 1.00         | n/a     | n/a          | n/a           | n/a           |
