#!/usr/bin/env python3

#This is a job launch script for boot tests

import os
import sys
from uuid import UUID

from gem5art.artifact.artifact import Artifact
from gem5art.run import gem5Run
from gem5art.tasks.tasks import run_gem5_instance

experiments_repo = Artifact.registerArtifact(
        command = 'git clone https://github.com/darchr/gem5art-experiments.git',
    typ = 'git repo',
    name = 'microbenchmark-tests',
    path =  './',
    cwd = '../',
    documentation = 'main experiments repo to run microbenchmarks with gem5'
)

gem5_repo = Artifact.registerArtifact(
    command = 'git clone https://github.com/darchr/gem5',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'git repo with gem5 master branch on Sep 23rd'
)

m5_binary = Artifact.registerArtifact(
    command = 'make -f Makefile.x86',
    typ = 'binary',
    name = 'm5',
    path =  'gem5/util/m5/m5',
    cwd = 'gem5/util/m5',
    inputs = [gem5_repo,],
    documentation = 'm5 utility'
)

gem5_binary = Artifact.registerArtifact(
    command = 'scons build/X86/gem5.opt',
    typ = 'gem5 binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'default gem5 x86'
)

if __name__ == "__main__":
    #boot_types = ['init', 'systemd']
    #num_cpus = ['1', '2', '4', '8']
    cpu_types = ['Simple','DefaultO3'] 
    mem_types = ['Slow']# [SingleCycle][Inf]
    full_list =['CCa','CCe','CCh', 'CCh_st', 'CCl','CCm','CF1','CRd','CRf','CRm',
    'CS1','CS3','DP1d','DP1f','DPcvt','DPT','DPTd','ED1','EF','EI','EM1','EM5',
    'MD' 'MC','MCS','M_Dyn','MI','MIM','MIM2','MIP','ML2','ML2_BW_ld','ML2_BW_ldst'
    'ML2_BW_st','ML2_st','MM','MM_st','STc','STL2','STL2b']
    controlbenchmarks = ['CCa','CCe','CCh', 'CCh_st', 'CCl','CCm','CF1','CRd','CRf','CRm',
    'CS1','CS3']
    memorybenchamarks = ['MD' 'MC','MCS','M_Dyn','MI','MIM','MIM2','MIP','ML2','ML2_BW_ld','ML2_BW_ldst'
    'ML2_BW_st','ML2_st']
    main_Memorybenchmarks = ['MM',' MM_st','STc','STL2','STL2b']

    bm_list = full_list

    #Architecture to run with.
    arch='X86' #'ARM'
    if arch =='X86':
        bma='bench.X86'
    elif arch =='ARM':
        bma='bench.ARM'
    path = 'microbench'

    for mem in mem_types:
        for bm in bm_list:
            for cpu in cpu_types:
                    run = gem5Run.createSERun(
                        'gem5/build/X86/gem5.opt',
                        'configs-microbench-tests/run_micro.py',
                        'allbenchmarks/results/{}/run_micro/{}/{}/{}'.format(arch,mem,bm,cpu),
                        gem5_binary, gem5_repo, experiments_repo,
                        cpu, mem, os.path.join(path,bm,bma))
                    #run_gem5_instance.apply_async((run,))
                    run.run()   
