#!/usr/bin/env python3

#This is a job launch script for boot tests

import os
import sys
from uuid import UUID

from gem5art.artifact.artifact import Artifact
from gem5art.run import gem5Run
from gem5art.tasks.tasks import run_gem5_instance

packer = Artifact.registerArtifact(
    command = '''wget https://releases.hashicorp.com/packer/1.4.3/packer_1.4.3_linux_amd64.zip;
    unzip packer_1.4.3_linux_amd64.zip;
    ''',
    typ = 'binary',
    name = 'packer',
    path =  'disk-image/packer',
    cwd = 'disk-image',
    documentation = 'Program to build disk images. Downloaded sometime in August from hashicorp.'
)

experiments_repo = Artifact.registerArtifact(
    command = 'git clone https://github.com/darchr/gem5art-experiments.git',
    typ = 'git repo',
    name = 'gapbs-test',
    path =  './',
    cwd = '../',
    documentation = 'main experiments repo to run GAPBS with gem5'
)

gem5_repo = Artifact.registerArtifact(
    command = 'git clone https://gem5.googlesource.com/public/gem5',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'cloned gem5 master branch from googlesource last commit was Feb 20, 2020'
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

disk_image = Artifact.registerArtifact(
    command = './packer build gapbs.json',
    typ = 'disk image',
    name = 'gapbs',
    cwd = 'disk-image',
    path = 'disk-image/gapbs-image/gapbs',
    inputs = [packer, experiments_repo, m5_binary,],
    documentation = 'Ubuntu with m5 binary installed and root auto login'
)

gem5_binary = Artifact.registerArtifact(
    command = '''cd gem5;
    scons build/X86/gem5.opt -j20
    ''',
    typ = 'gem5 binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'gem5 binary based on googlesource (Feb. 20, 2020)'
)

linux_repo = Artifact.registerArtifact(
    command = '''git clone https://github.com/torvalds/linux.git;
    mv linux linux-stable''',
    typ = 'git repo',
    name = 'linux-stable',
    path =  'linux-stable/',
    cwd = './',
    documentation = 'linux kernel 5.3.2 source code repo obtained in November 2019'
)


linux_binaries = Artifact.registerArtifact(
                name = 'vmlinux-5.2.3',
                typ = 'kernel',
                path = 'linux-stable/vmlinux-5.2.3',
                cwd = 'linux-stable/',
                command = '''git checkout v5.2.3;
                cp ../linux-configs/config.5.2.3 .config;
                make -j20;
                cp vmlinux vmlinux-5.2.3;
                ''',
                inputs = [experiments_repo, linux_repo,],
                documentation = "Kernel binary for 5.2.3 with simple "
                                 "config file",
        )

if __name__ == "__main__":
    
    num_cpus = ['1', '2', '4']
    workloads = ['bc', 'bfs', 'cc', 'sssp', 'tc','pr']
    sizes = ['10', '15', '20']
    graphs = ['roadU.sg', 'webU.sg']
    mem_types = ['classic', 'MI_example']

    for num_cpu in num_cpus:
        for workload in workloads:
            for size in sizes: 
                for mem in mem_types:
                    run = gem5Run.createFSRun(
                        'Running GAPBS',
                        'gem5/build/X86/gem5.opt',
                        'configs-gapbs-tests/gapbs_config.py',
                        'results/run_exit/vmlinux-5.2.3/gapbs/kvm/{}/{}/{}/synthetic/{}'.
                        format( num_cpu, mem ,workload, size),
                        gem5_binary, gem5_repo, experiments_repo,
                        'linux-stable/vmlinux-5.2.3',
                        'disk-image/gapbs-image/gapbs',
                        linux_binaries, disk_image, 'kvm', num_cpu, mem ,workload, '1', size,
                        timeout = 6*60*60 
                        )
                    run_gem5_instance(run,)
                            
    for num_cpu in num_cpus:
        for workload in workloads:
            for graph in graphs: 
                for mem in mem_types:
                    run = gem5Run.createFSRun(
                        'Running GAPBS',
                        'gem5/build/X86/gem5.opt',
                        'configs-gapbs-tests/gapbs_config.py',
                        'results/run_exit/vmlinux-5.2.3/gapbs/kvm/{}/{}/{}/realgraph/{}'.
                        format( num_cpu, mem ,workload, graph),
                        gem5_binary, gem5_repo, experiments_repo,
                        'linux-stable/vmlinux-5.2.3',
                        'disk-image/gapbs-image/gapbs',
                        linux_binaries, disk_image, 'kvm', num_cpu, mem ,workload, '0', graph,
                        timeout = 6*60*60 
                        )
                    run_gem5_instance(run,)
