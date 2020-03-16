#!/usr/bin/env python3

#This is a job launch script to run basic microbenchmark experiment for all cpu.

import os
import sys
import argparse
from uuid import UUID

from gem5art.artifact.artifact import Artifact
from gem5art.run import gem5Run
from gem5art.tasks.tasks import run_gem5_instance
import multiprocessing as mp

experiments_repo = Artifact.registerArtifact(
    command = 'git clone https://github.com/darchr/gem5art-experiments.git',
    typ = 'git repo',
    name = 'gem5art-experiments',
    path =  './',
    cwd = '../',
    documentation = 'main experiments repo to test gem5 with micro-benchmarks'
)

gem5_repo = Artifact.registerArtifact(
    command = '''git clone https://gem5.googlesource.com/public/gem5;
                 cd gem5;
                 git cherry-pick 27dbffdb006c7bd12ad2489a2d346274fe646720;
                 git cherry-pick ad65be829e7c6ffeaa143d292a7c4a5ba27c5c7c;
                 wget https://github.com/darchr/gem5/commit/f0a358ee08aba1563c7b5277866095b4cbb7c36d.patch;
                 git am f0a358ee08aba1563c7b5277866095b4cbb7c36d.patch --reject;
    ''',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'git repo with gem5 master branch, gem5 version - 19, cherry picks with BTB, branch direction patches and vector mem support'
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

run_scripts = Artifact.registerArtifact(
    command = 'wget https://github.com/darchr/gem5art/blob/master/docs/gem5-configs/configs-micro-tests/run_micro.py',
    typ = 'git repo',
    name = 'gem5-configs',
    path =  'gem5-configs',
    cwd = './',
    documentation = 'gem5 run scripts made specifically for micro-benchmarks benchmarks'
)

def worker(run):
    run.run()
    json = run.dumpsJson()
    print(json)

if __name__ == "__main__":

    # Types of CPUs cupported
    cpu_types = ['Simple','DefaultO3']

    # Types of memorys supported
    mem_types = ['Inf','SingleCycle','Slow']

    # All in benchmarks from VRG micro-benchmark suite
    micro_bm_list = ['CCa','CCe','CCh', 'CCh_st', 'CCl','CCm','CF1','CRd','CRf','CRm',
    'CS1','CS3','DP1d','DP1f','DPcvt','DPT','DPTd','ED1','EF','EI','EM1','EM5',
    'MD' 'MC','MCS','M_Dyn','MI','MIM','MIM2','MIP','ML2','ML2_BW_ld','ML2_BW_ldst'
    'ML2_BW_st','ML2_st','MM','MM_st','STc','STL2','STL2b']

    # List of control flow benchmarks
    control_bm_list = ['CCa','CCe','CCh', 'CCh_st', 'CCl','CCm','CF1','CRd','CRf','CRm',
    'CS1','CS3']
    # control_bm_list = ['CCa']

    # CPU configs with choice of predictor
    Simple_bp = ['Simple_Local', 'Simple_BiMode', 'Simple_Tournament', 'Simple_LTAGE']
    DefaultO3_bp= ['DefaultO3_Local' ,'DefaultO3_BiMode', 'DefaultO3_Tournament','DefaultO3_LTAGE']

    parser = argparse.ArgumentParser()
    parser.add_argument('--run', choices = ['all','sel'], default='all',help="Usage: --run = all (to run all config)\n\t --run = sel (to select config)")
    parser.add_argument('--cpu', choices = ['Simple','O3'], default='Simple',help="CPU type: must be one from this list ['Simple','O3']")
    parser.add_argument('--mem', choices = ['Inf','SingleCycle','Slow','all'], default='all',help="Memory type: must be one from this list ['Inf','SingleCycle','Slow']")
    args  = parser.parse_args()
    cpu_opt = args.cpu
    mem_opt = args.mem
    run_opt = args.run

    # Job queue
    jobs = []

    path = 'microbench'
  
    # Register the each benchmark used for test as an artifact
    for bm in control_bm_list:
        bm = Artifact.registerArtifact(
        command = '''
        cd microbench/{};
        make X86;
        '''.format(bm),
        typ = 'binary',
        name = bm,
        cwd = 'microbench/{}'.format(bm),
        path =  'microbench/{}/bench.X86'.format(bm),
        inputs = [experiments_repo,],
        documentation = 'microbenchmark ({}) binary for X86  ISA'.format(bm)
        )

    if (run_opt == 'all'): 
        mems = mem_types
        cpu_configs = Simple_bp + DefaultO3_bp
    elif (run_opt == 'sel'):
        if (cpu_opt == 'Simple'): cpu_configs = Simple_bp
        elif (cpu_opt == 'O3'): cpu_configs = DefaultO3_bp
        if (mem_opt == 'all'): mems = mem_types
        else : mems = [mem_opt]

    for mem in mems:
        for bm in control_bm_list:
            for cpu_config in cpu_configs:
                idx = cpu_config.find('_')
                cpu = cpu_config[:idx]
                bp = cpu_config[idx+1:]
                run = gem5Run.createSERun('X86_micro-benchmarks_control_flow__run_{}_{}_{}_{}'.format(bp,cpu,mem,bm),
                    'gem5/build/X86/gem5.opt',
                    'gem5-configs/configs-microbench-tests/run_controlbenchmarks.py',
                    'results/microbenchmark-experiments/control-flow/dev1/X86/{}/{}/{}/{}'.format(bp,cpu,mem,bm),
                    gem5_binary, gem5_repo, experiments_repo,
                    cpu_config, mem, os.path.join(path,bm,'bench.X86'))
                jobs.append(run)

    with mp.Pool(mp.cpu_count() // 8) as pool:
        pool.map(worker, jobs)  
