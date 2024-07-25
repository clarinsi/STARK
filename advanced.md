# Advanced settings
In addition to the [basic settings](settings.md), which can be used to define the trees under investigation and the associated information in the output, STARK also features some advanced settings aimed at optimizing its performance or addressing rare use cases. Please note that these were not extensively tested and should be used with caution.

## Large corpora

### `--continuation_processing `
**Value:** _yes, no_

This parameter can be used for running STARK on large corpora, as it performs intermittent storing of results for each of the subcorpora provided. To use it, the input folder must be structured the right way, e.g.

```bash
  -GF01
    -GF0148879-dedup.conllu
    -GF0151323-dedup.conllu
  -GF02
    -GF0231349-dedup.conllu
```

## Performance

### `--internal_saves`
**Value:** _\<path to folder for internal storage\>_

The optional `--internal_saves` parameter speeds up performance for users repeating several different queries on the same treebank, as it avoids repeating same parts of the execution twice. To test it, simply uncomment the parameter in the `config.ini` file or provide a different path for the internal data storage.

### `--cpu_cores`
**Value:** _\<integer number\>_

By default, STARK uses a single processor to execute. The optional `--cpu_core` parameter allows the users to define a specific number of processors to be used in the process, for example to boost the tool's performance by running it on all available CPU cores.

### `--greedy_counter`
**Values:** _yes, no_

The obligatory `--greedy_counter` parameter defines the way trees are extracted from the input treebank. The default is to use the so-called greedy counter (value _yes_), which searches the trees through a bottom-up approach based on the trees observed in the treebank. This is the recommended option for most use cases, especially if one is interested in longer trees as well. The alternative is using the so-called query counter (value _no_), which produces faster results when extracting trees based on [queries](settings.md#--query).


## Extracting incomplete trees

### `--complete`

**Values:** _yes, no_

The obligatory `--complete` parameter defines whether STARK, for a given tree size, should only extract complete trees encompassing the head and _all_ its (in)direct dependants (value _yes_), or all possible subtrees (paths) spanning from the head, i.e. all possible combinations of a head and its dependants (value _no_). Most use cases can be solved with the first option, so **`complete=yes` is the recommended default setting**. If you nevertheless decide to go with the `complete=no`, make sure to uncomment the `--processing_size` parameter (see below) and set it to a relatively low number (e.g. _2-7_), as only trees of limited size can be retrieved. In addition, we recommend increasing the [number of processor](#--cpu_cores) for even faster results.

### `--processing_size`

**Value:** _\<integer number or range\>_

By default, STARK searches for _all_ relevant trees based on the user-defined tree specifications and prints only those featuring the number of nodes specified by the [`--size`](settings.md\"--size) parameter, which means that it acts as a filter determining the size of the trees to be displayed. To also enable limiting the size of the trees to be extracted in the first place, the optional `--processing_size` parameter is introduced, which acts as a filter determining the size of the trees to be matched. Note that this is only relevant for the (rare) use cases interested in incomplete trees (see the [complete=no](#--complete) setting above). The recommended maximum size is 7 nodes or less.


## Debugging

### `--sentence_count_file `
**Value:** _\<path to file\>_

This parameter prints the number of occurrences of each tree in each sentence of the corpus. The lines in the output file give all sentence IDs, while the columns give the list of the output trees. Here is an example of the first few lines for the tree 'ADP <case DET <det PROPN':

```bash
weblog-blogspot.com_nominations_20041117172713_ENG_20041117_172713-0001	1
weblog-blogspot.com_nominations_20041117172713_ENG_20041117_172713-0002	0
weblog-blogspot.com_nominations_20041117172713_ENG_20041117_172713-0003	0
weblog-blogspot.com_nominations_20041117172713_ENG_20041117_172713-0004	0
weblog-blogspot.com_nominations_20041117172713_ENG_20041117_172713-0005	0
weblog-blogspot.com_gettingpolitical_20030906235000_ENG_20030906_235000-0001	0
weblog-blogspot.com_gettingpolitical_20030906235000_ENG_20030906_235000-0002	0
weblog-blogspot.com_gettingpolitical_20030906235000_ENG_20030906_235000-0003	0
weblog-blogspot.com_gettingpolitical_20030906235000_ENG_20030906_235000-0004	0
weblog-blogspot.com_gettingpolitical_20030906235000_ENG_20030906_235000-0005	0
```


### `--detailed_results_file `
**Value:** _\<path to file\>_

This parameter prints all the matched examples in the input treebank, i.e. all matched trees in all sentences, so it should be used with caution when large input treebanks are involved. Here is an example of the matched examples for tree 'PART \<mark VERB \>obl ADP':

```bash
(PART <mark VERB >obl ADP)ABC	reviews-139456-0001	Pleasure A[to] B[work] C[with]. 
(PART <mark VERB >obl ADP)ABC	reviews-114941-0003	They 're our favorite pizza place A[to] B[order] C[from]... and they 're a local, family owned company! 
(PART <mark VERB >obl ADP)ABC	reviews-351840-0002	We 've only had one urgent issue A[to] B[deal] C[with] and they were very prompt in their response. 
(PART <mark VERB >obl ADP)ABC	reviews-162702-0002	I was soooo lucky to have used Marlon 's photography services....such a creative and talented photographer and a pleasure A[to] B[work] C[with]. 
(PART <mark VERB >obl ADP)ABC	reviews-071017-0004	Hard A[to] B[get] C[into] though because of road construction. 
(PART <mark VERB >obl ADP)ABC	reviews-097507-0005	The owner/baker, "Pie Guy" is a hoot A[to] B[deal] C[with] as well. 
(PART <mark VERB >obl ADP)ABC	reviews-251475-0002	Best A[to] B[deal] C[with]! 
```

