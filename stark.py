import argparse
import configparser
import time
from pathlib import Path

import stark
# from stark.stark import read_configs, run


def parse_args():
    parser = argparse.ArgumentParser()

    ## Required parameters
    parser.add_argument("--config_file", default=str(Path.joinpath(Path(__file__).parent, "config.ini")), type=str,
                        help="The input config file.")
    parser.add_argument("--input", default=None, type=str, help="The input file/folder.")
    parser.add_argument("--output", default=None, type=str, help="The output file.")
    parser.add_argument("--internal_saves", default=None, type=str, help="Location for internal_saves.")
    parser.add_argument("--cpu_cores", default=None, type=int, help="Number of cores used.")

    parser.add_argument("--size", default=None, type=str, help="Size of trees.")
    parser.add_argument("--complete", default=None, type=str, help="Tree type.")
    parser.add_argument("--labeled", default=None, type=str, help="Dependency type.")
    parser.add_argument("--fixed", default=None, type=str, help="Order of node.")
    parser.add_argument("--node_type", default=None, type=str, help="Type of node.")

    parser.add_argument("--labels", default=None, type=str, help="Label whitelist.")
    parser.add_argument("--root", default=None, type=str, help="Root whitelist.")

    parser.add_argument("--query", default=None, type=str, help="Query.")

    parser.add_argument("--max_lines", default=None, type=str, help="Maximum number of trees in the output.")
    parser.add_argument("--frequency_threshold", default=None, type=int, help="Frequency threshold.")
    parser.add_argument("--association_measures", default=None, type=bool, help="Association measures.")
    parser.add_argument("--continuation_processing", default=None, type=bool, help="Nodes number.")
    parser.add_argument("--compare", default=None, type=str, help="Corpus with which we want to compare statistics.")
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    config = configparser.ConfigParser()
    config.read(args.config_file)

    configs = stark.read_configs(config, args)

    stark.run(configs)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Total:")
    print("--- %s seconds ---" % (time.time() - start_time))
