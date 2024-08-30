import os
import sys
import time
from pathlib import Path
import stark
from stark.stark import read_settings, parse_args
import logging
logger = logging.getLogger('stark')



# input_path = '/home/luka/Development/CJVT/STARK/data/ud-treebanks-v2.11/'
# output_path = '/home/luka/Development/CJVT/STARK/results/ud-treebanks-v2.11_B/'
# config_path = '/home/luka/Development/CJVT/STARK/data/B_test-all-treebanks_3_completed_unlabeled_fixed_form_root=NOUN_5.ini'
#
# for path in sorted(os.listdir(input_path)):
#     path_obj = Path(input_path, path)
#     pathlist = path_obj.glob('**/*.conllu')
#     for path in sorted(pathlist):
#         folder_name = os.path.join(output_path, path.parts[-2])
#         file_name = os.path.join(folder_name, path.name)
#         if not os.path.exists(folder_name):
#             os.makedirs(folder_name)
#         if not os.path.exists(file_name):
#             os.system("python /home/luka/Development/CJVT/STARK/stark.py --config_file " + config_path + " --input " + str(path) + " --output " + file_name)


def main():
    args = parse_args(sys.argv[1:])

    settings = read_settings(args.config_file, args)

    input_path = Path(settings['input_path'])
    output_path_parts = Path(settings['output']).parts

    # for path in sorted(os.listdir(settings['input_path'])):
    for path in sorted(input_path.rglob('*.conllu')):
        # create path to actual location
        relative_path_parts = path.parts[len(input_path.parts):]
        output_path = Path(*output_path_parts, *relative_path_parts)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not output_path.exists():
            logger.info(f'Processing file at: {path}')
            settings['input_path'] = str(path)
            settings['output'] = str(output_path)

            stark.run(settings)
        else:
            logger.info(f'Already processed, skipping: {path}')


if __name__ == "__main__":
    start_time = time.time()
    main()
    logger.info("Total:")
    logger.info("--- %s seconds ---" % (time.time() - start_time))

