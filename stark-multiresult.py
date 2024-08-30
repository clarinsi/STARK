import sys
import time
from pathlib import Path
import stark
from stark.stark import read_settings, parse_args
import logging
logger = logging.getLogger('stark')


def main():
    args = parse_args(sys.argv[1:])

    settings = read_settings(args.config_file, args)

    input_path = Path(settings['input_path'])
    output_path_parts = Path(settings['output']).parts

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
