#!/usr/bin/env python3

#This is a job launch script for boot tests with gem5-20

import os
import sys
from uuid import UUID
from itertools import starmap
from itertools import product

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
    command = 'git clone https://your-remote-add/boot_tests.git',
    typ = 'git repo',
    name = 'boot_tests',
    path =  './',
    cwd = '../',
    documentation = 'main experiments repo to run full system boot tests with gem5'
)

gem5_repo = Artifact.registerArtifact(
    command = 'git clone https://gem5.googlesource.com/public/gem5',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'cloned gem5 from googlesource and checked out release-staging-v20.0.0.0 (May 4, 2020)'
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
    command = './packer build boot-exit/boot-exit.json',
    typ = 'disk image',
    name = 'boot-disk',
    cwd = 'disk-image',
    path = 'disk-image/boot-exit/boot-exit-image/boot-exit',
    inputs = [packer, experiments_repo, m5_binary,],
    documentation = 'Ubuntu with m5 binary installed and root auto login'
)


ruby_mem_types = ['MI_example', 'MESI_Two_Level', 'MOESI_CMP_directory']
gem5_artifacts = {
        mem: Artifact.registerArtifact(
                command = f'''cd gem5;
                git checkout release-staging-v20.0.0.0;
                scons build/X86_{mem}/gem5.opt --default=X86 PROTOCOL={mem} -j8
                ''',
                typ = 'gem5 binary',
                name = f'gem5-{mem}',
                cwd = 'gem5/',
                path =  f'gem5/build/X86_{mem}/gem5.opt',
                inputs = [gem5_repo,],
                documentation = f'gem5 {mem} binary based on '
                    'googlesource/release-staging-v20.0.0.0 (April 4, 2020)'
                )
        for mem in ruby_mem_types
}

linux_repo = Artifact.registerArtifact(
    command = '''git clone https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git;
    mv linux linux-stable''',
    typ = 'git repo',
    name = 'linux-stable',
    path =  'linux-stable/',
    cwd = './',
    documentation = 'linux kernel source code repo downloaded in March 2020'
)

linuxes = ['5.4', '4.19.83', '4.14.134', '4.9.186', '4.4.186']
linux_binaries = {
    version: Artifact.registerArtifact(
                name = f'vmlinux-{version}',
                typ = 'kernel',
                path = f'linux-stable/vmlinux-{version}',
                cwd = 'linux-stable/',
                command = f'''git checkout v{version};
                cp ../linux-configs/config.{version} .config;
                make -j8;
                cp vmlinux vmlinux-{version};
                ''',
                inputs = [experiments_repo, linux_repo,],
                documentation = f"Kernel binary for {version} with simple "
                                 "config file",
            )
    for version in linuxes
}

if __name__ == "__main__":
    boot_types = ['init', 'systemd']
    num_cpus = ['1', '2', '4', '8']
    cpu_types = ['kvm', 'atomic', 'simple', 'o3']
    mem_types = ['classic'] + ruby_mem_types 

    def createRun(linux, boot_type, cpu, num_cpu, mem):

        if mem in gem5_artifacts:
            artifact_gem5 = gem5_artifacts[mem]
        else:
            # We can use any binary for classic
            artifact_gem5 = gem5_artifacts[ruby_mem_types[0]]
        
        binary_gem5 = artifact_gem5.path

        return gem5Run.createFSRun(
            'boot experiments with gem5-20',
            binary_gem5,
            'configs-boot-tests/run_exit.py',
            'results/run_exit/vmlinux-{}/boot-exit/{}/{}/{}/{}'.
                format(linux, cpu, mem, num_cpu, boot_type),
            artifact_gem5, gem5_repo, experiments_repo,
            os.path.join('linux-stable', 'vmlinux'+'-'+linux),
            'disk-image/boot-exit/boot-exit-image/boot-exit',
            linux_binaries[linux], disk_image,
            cpu, mem, num_cpu, boot_type,
            timeout = 6*60*60 #6 hours
            )

    # For the cross product of tests, create a run object.
    runs = starmap(createRun, product(linuxes, boot_types, cpu_types, num_cpus, mem_types)):
    # Run all of these experiments in parallel
    for run in runs:
        run_gem5_instance.apply_async((run, os.getcwd(),))
