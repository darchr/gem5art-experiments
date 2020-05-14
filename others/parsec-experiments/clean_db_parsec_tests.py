#!/usr/bin/env python3

from pymongo import MongoClient
from uuid import UUID

db = MongoClient().artifact_database


'''
This file updates the run object entries in the database,
so that the all (and only) valid runs have a name field
'name' = 'boot_tests_timeout'
'''

# Updating boot tests run objects with classic memory system


num_cpus = ['1']
benchmarks = ['blackscholes', 'bodytrack', 'canneal', 'dedup','facesim', 'ferret', 'fluidanimate', 'freqmine', 'raytrace', 'streamcluster', 'swaptions', 'vips', 'x264']

sizes = ['simsmall', 'simlarge', 'native']
cpus = ['kvm', 'timing']



for cpu in cpus:
	for num_cpu in num_cpus:
		for size in sizes:
			for bm in benchmarks:      
				db.artifacts.remove({'outdir':'/home/mahyar/Workplace/DArchR/gem5art-experiments/launch-scripts/results/run_parsec/{}/{}/{}'.format(bm, size, cpu)})
				