#!/usr/bin/env python3

import gem5art.run
import json
import sys

'''
Expects an input str = name of the experiments of interest
Generates a json file containing all the runs from that
experiment
'''

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print('Experiment Name (a string) Expected !!!!')
        exit()
    else:
        inp = str(sys.argv[1])

    jfile = open('runs.json', 'w')

    for i in gem5art.run.getRunsByName(name=inp, fs_only=False, limit=0):
        d = i._convertForJson(i._getSerializable())
        json.dump(d, jfile, indent=1)

