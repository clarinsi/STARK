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

This parameter prints the number of occurrences of each tree in each sentence of the corpus. Sentence IDs are listed as lines, and tree structures as columns.

### `--detailed_results_file `
**Value:** _\<path to file\>_

This parameter prints all the matched examples in the input treebank, i.e. all matched trees in all sentences, so it should be used with caution when large input treebanks are involved.

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
