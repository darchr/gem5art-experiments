#Copyright (c) 2020 The Regents of the University of California.
#All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


""" Script to run GAP Benchmark suites workloads. 
    The workloads have two modes: synthetic and real graphs.
"""

import sys
import time

import m5
import m5.ticks
from m5.objects import *

sys.path.append('gem5/configs/common/') # For the next line...
import SimpleOpts

from system import *

SimpleOpts.set_usage(
    "usage: %prog [options] kernel disk cpu_type num_cpus mem_sys benchmark synthetic graph")

SimpleOpts.add_option("--allow_listeners", default=False, action="store_true",
                      help="Listeners disabled by default")


def writeBenchScript(dir, benchmark_name, size, synthetic):
    """
    This method creates a script in dir which will be eventually
    passed to the simulated system (to run a specific benchmark
    at bootup).
    """
    input_file_name = '{}/run_{}_{}'.format(dir, benchmark_name, size)
    if (synthetic):
        with open(input_file_name,"w") as f:
           f.write('./{} -g {}\n'.format(benchmark_name, size))
    elif(synthetic==0):
        with open(input_file_name,"w") as f:
           f.write('#!/bin/sh\n')
           f.write('./{} -sf {}'.format(benchmark_name, size))
    
    return input_file_name

if __name__ == "__m5_main__":
    (opts, args) = SimpleOpts.parse_args()

    # create the system we are going to simulate
    if len(args) != 8:
        SimpleOpts.print_help()
        m5.fatal("Bad arguments")
    
    kernel, disk, cpu_type, num_cpus, mem_sys, benchmark, synthetic, benchmark_size = args
    num_cpus = int(num_cpus)

    if (mem_sys == "classic"):
        system = MySystem(kernel, disk, cpu_type, num_cpus,opts)
    elif (mem_sys == "MI_example"):
        system = MyRubySystem(kernel, disk, cpu_type, mem_sys, num_cpus,opts)

    
    system = MySystem(kernel, disk, cpu_type, num_cpus,opts)
    benchmark_name = benchmark

    output_dir = os.path.join(m5.options.outdir, "speclogs")

    # For workitems to work correctly
    # This will cause the simulator to exit simulation when the first work
    # item is reached and when the first work item is finished.
    system.work_begin_exit_count = 1
    system.work_end_exit_count = 1

    # Read in the script file passed in via an option.
    # This file gets read and executed by the simulated system after boot.
    # Note: The disk image needs to be configured to do this.

    system.readfile = writeBenchScript(m5.options.outdir, benchmark_name,
                                       benchmark_size, synthetic) 

    # set up the root SimObject and start the simulation
    root = Root(full_system = True, system = system)

    if system.getHostParallel():
        # Required for running kvm on multiple host cores.
        # Uses gem5's parallel event queue feature
        # Note: The simulator is quite picky about this number!
        root.sim_quantum = int(1e9) # 1 ms

    # instantiate all of the objects we've created above
        m5.instantiate()

    globalStart = time.time()


    print("Running the simulation")
    exit_event = m5.simulate()
    if exit_event.getCause() == "work started count reach":
        print("done")
