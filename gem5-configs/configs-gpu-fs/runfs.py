# -*- coding: utf-8 -*-
# Copyright (c) 2016 Jason Lowe-Power
# All rights reserved.
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
# Authors: Jason Lowe-Power
#          Pouya Fotouhi

""" Script to run X86 FS mode with support for Atomic, KVMm
    TimingSimple, and O3 CPUs. Suports only Ruby.
    Based on Jason Lowe-Power's FS mode scripts.
"""

import sys
import time

import m5
import m5.ticks
from m5.objects import *

#sys.path.append('configs')
#sys.path.append('configs/fs/system')
sys.path.append('gem5/configs/common/') # For the next lines
from common import SimpleOpts, Options, ObjectList
from system import MySystem
from ruby import Ruby

def addRunFSOptions(parser):
    parser.add_option("--cpu-type", type="choice",
                      choices=ObjectList.cpu_list.get_names(),
                      help = "type of cpu to run with")
    parser.add_option("--script", default='',
                      help="Script to execute in the simulated system")

    parser.add_option("--checkpoint", action="store_true",
                      help="Create checkpoint with KVM, otherwise restore")
    parser.add_option("--checkpoint-dir", type="string", default="m5out",
                      help="Directory to write/restore checkpoints from")
    parser.add_option("-r", "--checkpoint-restore", action="store", type="int",
                      help="restore from checkpoint <N>")

def addGPUOptions(parser):
    #######################
    #Copied from apu_se.py#
    #######################
    parser.add_option("--apu", action="store_true", default=False,
                      help="Configure the system as an APU")
    parser.add_option("--dgpu", action="store_true", default=False,
                      help="Configure the system as a dGPU instead of an APU.")

    parser.add_option("--cpu-only-mode", action="store_true", default=False,
                      help="APU mode. Used to take care of problems in "\
                           "Ruby.py while running APU protocols")
    parser.add_option("-u", "--num-compute-units", type="int", default=4,
                      help="number of GPU compute units"),
    parser.add_option("--num-cp", type="int", default=0,
                      help="Number of GPU Command Processors (CP)")
    parser.add_option("--benchmark-root",
                      help="Root of benchmark directory tree")

    # not super important now, but to avoid putting the number 4 everywhere,
    # make it an option/knob
    parser.add_option("--cu-per-sqc", type="int", default=4,
                      help="number of CUs sharing an SQC "
                      "(icache, and thus icache TLB)")
    parser.add_option('--cu-per-scalar-cache', type='int', default=4,
                      help='Number of CUs sharing a scalar cache')
    parser.add_option("--simds-per-cu", type="int", default=4,
                      help="SIMD units per CU")
    parser.add_option('--cu-per-sa', type='int', default=4,
                      help='Number of CUs per shader array. This must be a '
                      'multiple of options.cu-per-sqc '
                      'and options.cu-per-scalar')
    parser.add_option('--sa-per-complex', type='int', default=1,
                      help='Number of shader arrays per complex')
    parser.add_option('--num-gpu-complexes', type='int', default=1,
                      help='Number of GPU complexes')
    parser.add_option("--wf-size", type="int", default=64,
                      help="Wavefront size(in workitems)")
    parser.add_option("--sp-bypass-path-length", type="int", default=4, \
                      help="Number of stages of bypass path in vector ALU for "
                      "Single Precision ops")
    parser.add_option("--dp-bypass-path-length", type="int", default=4, \
                      help="Number of stages of bypass path in vector ALU for "
                      "Double Precision ops")
    # issue period per SIMD unit: number of cycles before issuing next vector
    parser.add_option("--issue-period", type="int", default=4, \
                      help="Number of cycles per vector instruction issue "
                      "period")
    parser.add_option("--glbmem-wr-bus-width", type="int", default=32, \
                      help="VGPR to Coalescer (Global Memory) data bus width "
                      "in bytes")
    parser.add_option("--glbmem-rd-bus-width", type="int", default=32, \
                      help="Coalescer to VGPR (Global Memory) data bus width "
                      "in bytes")
    # Currently we only support 1 local memory pipe
    parser.add_option("--shr-mem-pipes-per-cu", type="int", default=1, \
                      help="Number of Shared Memory pipelines per CU")
    # Currently we only support 1 global memory pipe
    parser.add_option("--glb-mem-pipes-per-cu", type="int", default=1, \
                      help="Number of Global Memory pipelines per CU")
    parser.add_option("--wfs-per-simd", type="int", default=10,
                      help="Number of WF slots per SIMD")

    parser.add_option("--registerManagerPolicy", type="string",
                      default="static",
                      help="Register manager policy")
    parser.add_option("--vreg-file-size", type="int", default=2048,
                      help="number of physical vector registers per SIMD")
    parser.add_option("--vreg-min-alloc", type="int", default=4,
                      help="Minimum number of registers that can be allocated "
                      "from the VRF. The total number of registers will be "
                      "aligned to this value.")

    parser.add_option("--sreg-file-size", type="int", default=2048,
                      help="number of physical vector registers per SIMD")
    parser.add_option("--sreg-min-alloc", type="int", default=4,
                      help="Minimum number of registers that can be allocated "
                      "from the SRF. The total number of registers will be "
                      "aligned to this value.")

    parser.add_option("--bw-scalor", type="int", default=0,
                      help="bandwidth scalor for scalability analysis")
    parser.add_option("--CPUClock", type="string", default="2GHz",
                      help="CPU clock")
    parser.add_option("--gpu-clock", type="string", default="1GHz",
                      help="GPU clock")
    parser.add_option("--cpu-voltage", action="store", type="string",
                      default='1.0V',
                      help = """CPU  voltage domain""")
    parser.add_option("--gpu-voltage", action="store", type="string",
                      default='1.0V',
                      help = """CPU  voltage domain""")
    parser.add_option("--CUExecPolicy", type="string", default="OLDEST-FIRST",
                      help="WF exec policy (OLDEST-FIRST, ROUND-ROBIN)")
    parser.add_option("--SegFaultDebug",action="store_true",
                     help="checks for GPU seg fault before TLB access")
    parser.add_option("--FunctionalTLB",action="store_true",
                     help="Assumes TLB has no latency")
    parser.add_option("--LocalMemBarrier",action="store_true", help="Barrier "
                      "does not wait for writethroughs to complete")
    parser.add_option("--countPages", action="store_true", help="Count Page "
                      "Accesses and output in per-CU output files")
    parser.add_option("--TLB-prefetch", type="int", help = "prefetch depth "
                      "for TLBs")
    parser.add_option("--pf-type", type="string", help="type of prefetch: "\
                      "PF_CU, PF_WF, PF_PHASE, PF_STRIDE")
    parser.add_option("--pf-stride", type="int", help="set prefetch stride")
    parser.add_option("--numLdsBanks", type="int", default=32,
                      help="number of physical banks per LDS module")
    parser.add_option("--ldsBankConflictPenalty", type="int", default=1,
                      help="number of cycles per LDS bank conflict")
    parser.add_option('--fast-forward-pseudo-op', action='store_true',
                      help = 'fast forward using kvm until the m5_switchcpu'
                      ' pseudo-op is encountered, then switch cpus. subsequent'
                      ' m5_switchcpu pseudo-ops will toggle back and forth')
    parser.add_option("--num-hw-queues", type="int", default=10,
                      help="number of hw queues in packet processor")


def runFullSystem():
    (opts, args) = SimpleOpts.parse_args()
    kernel, disk, cpu, benchmark, num_cpus = args

    # Don't init GPU stuff in Ruby if no GPU is specified
    if opts.dgpu or opts.apu:
        opts.cpu_only_mode = False
    else:
        opts.cpu_only_mode = True

    # create the system we are going to simulate
    system = MySystem(kernel, disk, int(num_cpus), opts, no_kvm=False)

    # Exit from guest on workbegin/workend
    system.exit_on_work_items = True

    # Set up the root SimObject and start the simulation
    root = Root(full_system = True, system = system)

    if system.getHostParallel():
        # Required for running kvm on multiple host cores.
        # Uses gem5's parallel event queue feature
        # Note: The simulator is quite picky about this number!
        root.sim_quantum = int(1e9) # 1 ms

    # Instantiate all of the objects
    if opts.checkpoint_restore:
        m5.instantiate(opts.checkpoint_dir)
    else:
        m5.instantiate()

    globalStart = time.time()

    print("Running the simulation")
    print("Using cpu: {}".format(cpu))
    exit_event = m5.simulate(opts.abs_max_tick)

    # While there is still something to do in the guest keep executing.
    while exit_event.getCause() != "m5_exit instruction encountered":
        # If the user pressed ctrl-c on the host, then we really should exit
        if exit_event.getCause() == "user interrupt received":
            print("User interrupt. Exiting")
            break

        if exit_event.getCause() == "simulate() limit reached":
            break
        elif "checkpoint" in exit_event.getCause():
            m5.checkpoint(opts.checkpoint_dir)
            break
        elif "switchcpu" in exit_event.getCause():
            system.switchCpus(system.cpu, system.warmupCpu)
        else:
            break

    print('Exiting @ tick %i because %s' %
          (m5.curTick(), exit_event.getCause()))

if __name__ == "__m5_main__":
        addRunFSOptions(SimpleOpts)
        addGPUOptions(SimpleOpts)
        Options.addNoISAOptions(SimpleOpts)
        Ruby.define_options(SimpleOpts)
        runFullSystem()
