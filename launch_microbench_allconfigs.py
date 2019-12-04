#!/usr/bin/env python3

#This is a job launch script

import os
import sys
from uuid import UUID

from gem5art.artifact.artifact import Artifact
from gem5art.run import gem5Run
from gem5art import tasks


experiments_repo = Artifact.registerArtifact(
    command = 'git clone https://github.com/darchr/gem5art-experiments.git',
    typ = 'git repo',
    name = 'gem5-experiments',
    path =  './',
    cwd = '../',
    documentation = 'main experiments repo to run experiments in gem5art'
)

gem5_repo = Artifact.registerArtifact(
    command = 'git clone https://github.com/darchr/gem5',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'git repo with gem5 master branch '
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
    typ = 'binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'default gem5 x86'
)

if __name__ == "__main__":
    
    num_cpus = ['1']#, '2', '4', '8']
    cpu_types = ['Simple','DefaultO3'] 
    #mem_types = ['classic']#, 'ruby']
    mem_latency = ['Inf','SingleCycle'] #, 'Slow', 'Inf' 'SingleCycle']
    config='config1' #'config2''config3'

    full_list =['CCa','CCe','CCh', 'CCh_st', 'CCl','CCm','CF1','CRd','CRf','CRm',
    'CS1','CS3','DP1d','DP1f','DPcvt','DPT','DPTd','ED1','EF','EI','EM1','EM5',
    'MD','MC','MCS','M_Dyn','MI','MIM','MIM2','MIP','ML2','ML2_BW_ld','ML2_BW_ldst',
    'ML2_BW_st','ML2_st','MM','MM_st','STc','STL2','STL2b']
    controlbenchmarks = ['CCa','CCe','CCh', 'CCh_st','CCl','CCm','CF1','CRd','CRf','CRm',
    'CS1','CS3']
    memorybenchmarks = ['MD','MC','MCS','M_Dyn','MI','MIM','MIM2','MIP','ML2','ML2_BW_ld','ML2_BW_ldst',
    'ML2_BW_st','ML2_st','MM','MM_st','STc','STL2','STL2b']
    main_Memorybenchmarks = []
    bm_list = full_list
L1Cache_sizes
    #Branchpredictors for cpus
    cpu_bp='Simple' #O3
    Simple_bp=('Simple_Local', 'Simple_BiMode', 'Simple_Tournament', 'Simple_LTAGE')
    DefaultO3_bp=('DefaultO3_Local' ,'DefaultO3_BiMode', 'DefaultO3_Tournament','DefaultO3_LTAGE')
    
    cache_type = 'L1_cache' #'L2_cache'
    #L1Cache_sizes.
    L1D = ['4kB','32kB','64kB']
    #L2Cache_sizes.
    L2C = ['512kB','1MB']

    #Architecture to run with.
    arch='X86' #'ARM'
    if arch =='X86':
        bma='bench.X86'
    elif arch =='ARM':
        bma='bench.ARM'

    path = 'microbench'
    
    if config == 'config1':
      for mem in mem_latency:
        for bm in bm_list:
            for cpu in cpu_types:
                    run = gem5Run.createSERun(
                        'gem5/build/X86/gem5.opt',
                        'configs-microbench-tests/run_allbenchmarks.py',
                        'results/{}/run_config1/{}/{}/{}'.format(arch,mem,bm,cpu),
                        gem5_binary, gem5_repo, experiments_repo,
                        cpu, mem, os.path.join(path,bm,bma))
                    #run_gem5_instance.apply_async((run,))
                    run.run() 
    elif config == 'config2':
        for mem in mem_latency:
            for bm in bm_list:
                if cpu_bp == 'Simple':
                    for config_cpu in Simple_bp:
                        run = gem5Run.createSERun(
                                'gem5/build/X86/gem5.opt',
                                'configs-microbench-tests/run_controlbenchmarks.py',
                                'results/{}/run_config2/{}/{}/{}/{}'.format(arch,mem,bm,cpu_bp,config_cpu), 
                                gem5_binary, gem5_repo, experiments_repo,
                                config_cpu, mem, os.path.join(path,bm,bma))
                        #run_gem5_instance.apply_async((run,)) 
                        run.run()  
                elif cpu_bp == 'O3':
                    for config_cpu in  DefaultO3_bp:
                        run = gem5Run.createSERun(
                                'gem5/build/X86/gem5.opt',
                                'configs-microbench-tests/run_controlbenchmarks.py',
                                'results/{}/run_config2/{}/{}/{}/{}'.format(arch,mem,bm,cpu_bp,config_cpu), 
                                gem5_binary, gem5_repo, experiments_repo,
                                config_cpu, mem, os.path.join(path,bm,bma))
                        #run_gem5_instance.apply_async((run,))
                        run.run()
    elif config =='config3':
        for mem in mem_latency:
            for bm  in bm_list:
                for cpu in cpu_types:
                        if cache_type =='L1_cache':
                            for size in L1D:
                                run = gem5Run.createSERun(
                                'gem5/build/X86/gem5.opt',
                                'configs-microbench-tests/run_memorybenchmarks.py',
                                'results/{}/run_config3/{}/{}/{}/L1_cache/{}'.format(arch,mem,bm,cpu,size), 
                                gem5_binary, gem5_repo, experiments_repo,
                                cpu, mem, size,'1MB', os.path.join(path,bm,bma))
                                #run_gem5_instance.apply_async((run,))
                                run.run()
                        if cache_type=='L2_cache':
                            for size in L2C:
                                run = gem5Run.createSERun(
                                'gem5/build/X86/gem5.opt',
                                'configs-microbench-tests/run_memorybenchmarks.py',
                                'results/{}/run_config3/{}/{}/{}/L2_cache/{}'.format(arch,mem,bm,cpu,size), 
                                gem5_binary, gem5_repo, experiments_repo,
                                cpu, mem,'32kB',size, os.path.join(path,bm,bma))
                                #run_gem5_instance.apply_async((run,))
                                run.run()


                

    



    

