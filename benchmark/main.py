import pandas as pd
#import argparse
import os
import git
import hashlib
import time

def main():
    path_list = ["benchmark", "data"]
    path = os.sep.join(path_list)
    if not (os.path.exists(path) and os.path.isdir(path)):
        os.mkdir(path)
    path_list.append("speed.tsv")
    path = os.sep.join(path_list)

    if os.path.exists(path) and os.path.isfile(path):
        df = pd.read_csv(path, encoding="utf-8", sep="\t")
    else:
        df = pd.DataFrame(columns=["commit", "time", "output_sha256"])

    repo = git.Repo()
    commit_sha = repo.head.object.hexsha
    
    t_start = time.time()

    prcs_res = os.system(f"python3 -OO stark.py --config_file benchmark{os.sep}config_benchmark.ini")
    #prcs_res = os.system(f"pypy -OO stark.py --config_file benchmark{os.sep}config_benchmark.ini")
    if prcs_res != 0:
        raise Exception(f"prcs_res: {prcs_res}")

    t_end = time.time()
    t_delta = t_end - t_start


    path_list.pop()
    path_list.append("output.tsv")
    path_stark_output = os.sep.join(path_list)

    h = hashlib.sha256()

    f = open(path_stark_output, "rb")

    while True:
        x = f.read(65536)
        if not x:
            break
        h.update(x)

    f.close()

    new_df = pd.DataFrame([{"commit": commit_sha, "time": t_delta, "output_sha256": h.hexdigest()}])

    df = pd.concat([df, new_df], ignore_index=True)

    df.to_csv(path, encoding="utf-8", sep="\t", index=False)

    print(f"Updated {repr(path)}")

    return 0

if __name__ == "__main__":
    exit(main())
