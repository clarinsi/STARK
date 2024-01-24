
### `--internal_saves`
**Value:** _\<path to folder for internal storage\>_

The optional `--internal_saves` parameter speeds up performance for users repeating several different queries on the same treebank, as it avoids repeating same parts of the execution twice. To test it, simply uncomment the parameter in the `config.ini` file or provide a different path for the internal data storage.

### `--cpu_cores`
**Value:** _\<integer number\>_

By default, STARK uses all available processors except one. The optional `--cpu_core` parameter allows the users to define a specific number of processors to be used in the process, for example to boost the tool's performance by running it on all available CPU cores.

### `--sentence_count_file `
TBA

### `--detailed_results_file ` 
TBA

### `--continuation_processing `
TBA
