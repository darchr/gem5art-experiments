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
    command = 'git clone https://your-remote-add/npb-tests.git',
    typ = 'git repo',
    name = 'npb_tests',
    path =  './',
    cwd = '../',
    documentation = 'main repo to run npb multicore tests with gem5 20'
)

gem5_repo = Artifact.registerArtifact(
    command = 'git clone https://gem5.googlesource.com/public/gem5',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'cloned gem5 from googlesource and checked out release-staging-v20.0.0.0 (May 10, 2020)'
)

m5_binary = Artifact.registerArtifact(
    command = 'scons build/x86/out/m5',
    typ = 'binary',
    name = 'm5',
    path =  'gem5/util/m5/build/x86/out/m5',
    cwd = 'gem5/util/m5',
    inputs = [gem5_repo,],
    documentation = 'm5 utility with gem5-20'
)

disk_image = Artifact.registerArtifact(
    command = './packer build npb/npb.json',
    typ = 'disk image',
    name = 'npb',
    cwd = 'disk-image',
    path = 'disk-image/npb/npb-image/npb',
    inputs = [packer, experiments_repo, m5_binary,],
    documentation = 'Ubuntu with m5 binary and NPB (with ROI annotations: darchr/npb-hooks/master) installed.'
)

gem5_binary = Artifact.registerArtifact(
    command = '''cd gem5;
    git checkout 97d45c5dc70ab50e6273fb,
    scons build/X86/gem5.opt -j8,
    ''',
    typ = 'gem5 binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'gem5 binary based on googlesource/release-staging-v20.0.0.0 (May 10, 2020)'
)

gem5_binary_MESI_Two_Level = Artifact.registerArtifact(
    command = '''cd gem5;
    git checkout release-staging-v20.0.0.0;
    scons build/MOESI_CMP_directory/gem5.opt --default=X86 PROTOCOL=MESI_Two_Level -j8
    ''',
    typ = 'gem5 binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86_MESI_Two_Level/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'gem5 binary based on googlesource/release-staging-v20.0.0.0 (May 10, 2020)'
)

linux_repo = Artifact.registerArtifact(
    command = '''git clone --branch v4.19.83 --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git;
    mv linux linux-stable''',
    typ = 'git repo',
    name = 'linux-stable',
    path =  'linux-stable/',
    cwd = './',
    documentation = 'linux kernel source code repo'
)

linux_binary = Artifact.registerArtifact(
    name = 'vmlinux-4.19.83',
    typ = 'kernel',
    path = 'linux-stable/vmlinux-4.19.83',
    cwd = 'linux-stable/',
    command = '''
    cp ../config.4.19.83 .config;
    make -j8;
    cp vmlinux vmlinux-4.19.83;
    ''',
    inputs = [experiments_repo, linux_repo,],
    documentation = "kernel binary for v4.19.83",
)


if __name__ == "__main__":
    num_cpus = ['1', '8']
    benchmarks = ['is.x', 'ep.x', 'cg.x', 'mg.x','ft.x', 'bt.x', 'sp.x', 'lu.x']

    classes = ['A']
    mem_sys = ['classic', 'MESI_Two_Level']
    cpus = ['kvm', 'timing']


    def createRun(bench, clas, cpu, mem, num_cpu):

        if mem == 'MESI_Two_Level':
            binary_gem5 = 'gem5/build/X86_MESI_Two_Level/gem5.opt'
            artifact_gem5 = gem5_binary_MESI_Two_Level
        else:
            binary_gem5 = 'gem5/build/X86/gem5.opt'
            artifact_gem5 = gem5_binary

        return gem5Run.createFSRun(
            'npb_multicore_tests with gem5-20',    
            binary_gem5,
            'configs-npb-tests-multicore-new/run_npb_multicore.py',
            f'''results/run_npb_multicore/{bench}/{clas}/{cpu}/{num_cpu}''',
            artifact_gem5, gem5_repo, experiments_repo,
            'linux-stable/vmlinux-4.19.83',
            'disk-image/npb/npb-image/npb',
            linux_binary, disk_image,
            cpu, mem, bench.replace('.x', f'.{clas}.x'), num_cpu,
            timeout = 240*60*60 #240 hours
            )


    # For the cross product of tests, create a run object.
    runs = starmap(createRun, product(benchmarks, classes, cpus, mem_sys, num_cpus))
    # Run all of these experiments in parallel
    for run in runs:
        run_gem5_instance.apply_async((run, os.getcwd(),))
