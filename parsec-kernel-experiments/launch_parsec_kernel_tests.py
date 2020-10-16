import os
import sys
from uuid import UUID
from itertools import starmap
from itertools import product

from gem5art.artifact import Artifact
from gem5art.run import gem5Run
from gem5art.tasks.tasks import run_gem5_instance, run_job_pool

experiments_repo = Artifact.registerArtifact(
    command = 'git clone https://github.com/darchr/gem5art-experiments.git',
    typ = 'git repo',
    name = 'parsec_kernel_tests',
    path =  './',
    cwd = '../',
    documentation = 'main repo to run parsec tests with gem5v20.1'
)

gem5_repo = Artifact.registerArtifact(
    command = '''
        git clone https://gem5.googlesource.com/public/gem5;
    ''',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'cloned gem5v20.1 from the google repository'
)

m5_binary = Artifact.registerArtifact(
    command = 'scons build/x86/out/m5',
    typ = 'binary',
    name = 'm5',
    path =  'gem5/util/m5/build/x86/out/m5',
    cwd = 'gem5/util/m5',
    inputs = [gem5_repo,],
    documentation = 'm5 utility'
)

disk_image_u18 = Artifact.registerArtifact(
    command = './packer build parsec-u18.04/parsec.json',
    typ = 'disk image',
    name = 'parsec-u18.04',
    cwd = 'disk-images',
    path = 'disk-images/parsec-u18.04/parsec-image/parsec-u18.04',
    inputs = [experiments_repo, m5_binary,],
    documentation = 'Disk-image using Ubuntu 18.04 with m5 binary and PARSEC installed.'
)

disk_image_u20 = Artifact.registerArtifact(
    command = './packer build parsec-u20.04/parsec.json',
    typ = 'disk image',
    name = 'parsec-u20.0',
    cwd = 'disk-images',
    path = 'disk-images/parsec-u20.04/parsec-image/parsec-u20.04',
    inputs = [experiments_repo, m5_binary,],
    documentation = 'Disk-image using Ubuntu 20.04 with m5 binary and PARSEC installed.'
)

gem5_binary = Artifact.registerArtifact(
    command = 'scons build/X86_MESI_Two_Level/gem5.opt -j12',
    typ = 'gem5 binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86_MESI_Two_Level/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'gem5 binary'
)

linux_repo_4 = Artifact.registerArtifact(
    command = '''git clone --branch v4.15.18 --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git;
    mv linux linux_4.15.18''',
    typ = 'git repo',
    name = 'linux-stable_4',
    path =  'linux-stable/linux_4.15.18/',
    cwd = './',
    documentation = 'linux kernel source code repo'
)

linux_repo_5 = Artifact.registerArtifact(
    command = '''git clone --branch v5.4.51 --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git;
    mv linux linux_5.4.51''',
    typ = 'git repo',
    name = 'linux-stable_5',
    path =  'linux-stable/linux_5.4.51/',
    cwd = './',
    documentation = 'linux kernel source code repo'
)


linux_binary_4 = Artifact.registerArtifact(
    name = 'vmlinux-4.15.18',
    typ = 'kernel',
    path = 'linux-stable/linux_4.15.18/vmlinux-4.15.18',
    cwd = 'linux-stable/',
    command = '''
    cp ../../config.4.15.18 .config;
    make -j30;
    cp vmlinux vmlinux-4.15.18;
    ''',
    inputs = [experiments_repo, linux_repo_4,],
    documentation = "kernel binary for v4.15.18"
)

linux_binary_5 = Artifact.registerArtifact(
    name = 'vmlinux-5.4.51',
    typ = 'kernel',
    path = 'linux-stable/linux_5.4.51/vmlinux-5.4.51',
    cwd = 'linux-stable/',
    command = '''
    cp ../../../config.5.4.51 .config;
    make -j30;
    cp vmlinux vmlinux-5.4.51;
    ''',
    inputs = [experiments_repo, linux_repo_5,],
    documentation = "kernel binary for v5.4.51"
)


if __name__ == "__main__":

    benchmarks = ['vips']
    sizes = ['simsmall', 'simmedium']
    cpus = ['kvm', 'simple']
    num_cpus = ['1', '2', '8']

    def createRun(image, kernel, bench, size, cpu, cores):
        return gem5Run.createFSRun(
            'os comparison tests (vips-real-fix)',
            'gem5/build/X86_MESI_Two_Level/gem5.opt',
            'configs-mesi-two-level/run_parsec_mesi_two_level.py',
            f'''results_vips_fixed/{image.name}/{cpu}/{cores}/{bench}/{size}''',
            gem5_binary, gem5_repo, experiments_repo,
            kernel.path,
            image.path,
            kernel, image,
            cpu, bench, size, cores,
            timeout = 20*60*60 #20 hours
            )
    # For the cross product of tests, create a run object.
    u18_runs = starmap(createRun, product([disk_image_u18], [linux_binary_4], benchmarks, sizes, cpus, num_cpus))
    u20_runs = starmap(createRun, product([disk_image_u20], [linux_binary_5], benchmarks, sizes, cpus, num_cpus))

    # Run all of these experiments in parallel
    # runs = [timing_runs , kvm_runs]
    # for run in runs:
    #     run_gem5_instance.apply_async((run, os.getcwd(),))
    runs = list(u18_runs) + list(u20_runs)

    run_job_pool(list(runs), num_parallel_jobs = 12)
