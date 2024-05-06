import argparse
import configparser
import sys
import time
from pathlib import Path

import stark
from stark.stark import read_settings, parse_args


def main():
    args = parse_args(sys.argv[1:])

    settings = read_settings(args.config_file, args)

    stark.run(settings)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Total:")
    print("--- %s seconds ---" % (time.time() - start_time))
