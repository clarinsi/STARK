# Statistics explained

By default, STARK produces a list of trees with the **absolute frequency** (raw count) and the **relative frequency** (normalized count per million tokens) of the trees in the input treebank. In addition, two optional types of statistics can also be computed in the output to help identify compelling syntactic phenomena: **association measures** and **keyness measures**.

## Association measures

Association measures, also known as collocation scores, are statistical tools used to evaluate the strength of association between words in a corpus. They compare the observed frequency of a word pair (or n-gram) with its expected frequency under the assumption of independence. Below is the list of association measures used in STARK along with their corresponding equations, where trees serve as the sequences of interest and nodes as their constituent elements.

### Data points

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
