import os
from pathlib import Path

input_path = '/home/lukakrsnik/STARK/data/ud-treebanks-v2.11/'
output_path = '/home/lukakrsnik/STARK/results/ud-treebanks-v2.11_B/'
config_path = '/home/lukakrsnik/STARK/data/B_test-all-treebanks_3_completed_unlabeled_fixed_form_root=NOUN_5.ini'

for path in sorted(os.listdir(input_path)):
    path_obj = Path(input_path, path)
    pathlist = path_obj.glob('**/*.conllu')
    for path in sorted(pathlist):
        folder_name = os.path.join(output_path, path.parts[-2])
        file_name = os.path.join(folder_name, path.name)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        if not os.path.exists(file_name):
            os.system("python /home/luka/Development/STARK/dependency-parsetree.py --config_file " + config_path + " --input " + str(path) + " --output " + file_name)
