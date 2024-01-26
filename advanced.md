# Advanced settings
In addition to the [basic settings](settings.md), which can be used to define the trees under investigation and the associated information in the output, STARK also features some advanced settings aimed at optimizing its performance. Please note that these were not extensively tested and should be used with caution.

## Performance

### `--internal_saves`
**Value:** _\<path to folder for internal storage\>_

The optional `--internal_saves` parameter speeds up performance for users repeating several different queries on the same treebank, as it avoids repeating same parts of the execution twice. To test it, simply uncomment the parameter in the `config.ini` file or provide a different path for the internal data storage.

### `--cpu_cores`
**Value:** _\<integer number\>_

By default, STARK uses all available processors except one. The optional `--cpu_core` parameter allows the users to define a specific number of processors to be used in the process, for example to boost the tool's performance by running it on all available CPU cores.

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

This parameter prints all the matched examples in the input treebank, i.e. all matched trees in all sentences, so it should be used with caution when large input treebanks are involved. Here is an example of the matched examples for tree 'PART <mark VERB >obl ADP':

```bash
(PART <mark VERB >obl ADP)ABC	reviews-139456-0001	Pleasure A[to] B[work] C[with]. 
(PART <mark VERB >obl ADP)ABC	reviews-114941-0003	They 're our favorite pizza place A[to] B[order] C[from]... and they 're a local, family owned company! 
(PART <mark VERB >obl ADP)ABC	reviews-351840-0002	We 've only had one urgent issue A[to] B[deal] C[with] and they were very prompt in their response. 
(PART <mark VERB >obl ADP)ABC	reviews-162702-0002	I was soooo lucky to have used Marlon 's photography services....such a creative and talented photographer and a pleasure A[to] B[work] C[with]. 
(PART <mark VERB >obl ADP)ABC	reviews-071017-0004	Hard A[to] B[get] C[into] though because of road construction. 
(PART <mark VERB >obl ADP)ABC	reviews-097507-0005	The owner/baker, "Pie Guy" is a hoot A[to] B[deal] C[with] as well. 
(PART <mark VERB >obl ADP)ABC	reviews-251475-0002	Best A[to] B[deal] C[with]! 
```

## Large corpora

### `--continuation_processing `
**Value:** _\<path to folder with corpus files\>_

This parameter can be used for running STARK on large corpora, as it performs intermittent storing of results for each of the subcorpora provided. To use it, the input folder must be structured the right way, e.g.
Gigafida

```bash
  -GF01
    -GF0148879-dedup.conllu
    -GF0151323-dedup.conllu
  -GF02
    -GF0231349-dedup.conllu
```
