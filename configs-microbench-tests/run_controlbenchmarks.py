# -*- coding: utf-8 -*-
# Copyright (c) 2018 The Regents of the University of California
# All Rights Reserved.
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

from __future__ import print_function

import argparse
import m5
from m5.objects import TimingSimpleCPU, DerivO3CPU
from m5.objects import SimpleIndirectPredictor, LocalBP, BiModeBP, TournamentBP, LTAGE, SimpleMemory
from m5.objects import Root
from m5.objects import *

from system import BaseTestSystem

#CPU Configs
class Simple_LocalBP(TimingSimpleCPU):
    branchPred = LocalBP()

class Simple_BiModeBP(TimingSimpleCPU):
    branchPred = BiModeBP()
    
class Simple_TournamentBP(TimingSimpleCPU):
    branchPred = TournamentBP()
    
class Simple_LTAGEBP(TimingSimpleCPU):
    branchPred = LTAGE()

class DefaultO3_LocalBP(DerivO3CPU):
    branchPred = LocalBP()

class DefaultO3_BiModeBP(DerivO3CPU):
    branchPred = BiModeBP()

class DefaultO3_TournamentBP(DerivO3CPU):
    branchPred = TournamentBP()

class DefaultO3_LTAGEBP(DerivO3CPU):
    branchPred = LTAGE()





# Add more CPUs Configs under test before this
valid_configs = [Simple_LocalBP, Simple_BiModeBP, Simple_TournamentBP, Simple_LTAGEBP, DefaultO3_LocalBP, DefaultO3_BiModeBP, DefaultO3_TournamentBP, DefaultO3_LTAGEBP]
valid_configs = {cls.__name__[:-2]:cls for cls in valid_configs}

#valid_cpus = {cls.__name__[:-3]:cls for cls in valid_cpus}

class InfMemory(SimpleMemory):
    latency = '0ns'
    bandwidth = '0B/s'

class SingleCycleMemory(SimpleMemory):
    latency = '1ns'
    bandwidth = '0B/s'

class SlowMemory(SimpleMemory):
    latency = '100ns'
    bandwidth = '0B/s'
     
class RealisticMemory:
    dummy = None

# Add more Memories under test before this
valid_memories = [InfMemory, SingleCycleMemory, SlowMemory, RealisticMemory]
valid_memories = {cls.__name__[:-6]:cls for cls in valid_memories}

parser = argparse.ArgumentParser()
parser.add_argument('config', choices = valid_configs.keys())
parser.add_argument('memory_model', choices = valid_memories.keys())
parser.add_argument('binary', type = str, help = "Path to binary to run")
args = parser.parse_args()


class MySystem(BaseTestSystem):
    _CPUModel = valid_configs[args.config]
    _MemoryModel = valid_memories[args.memory_model]
system = MySystem()

system.setTestBinary(args.binary)

root = Root(full_system = False, system = system)
m5.instantiate()

exit_event = m5.simulate()

if exit_event.getCause() != 'exiting with last active thread context':
    print("Benchmark failed with bad exit cause.")
    print(exit_event.getCause())
    exit(1)
if exit_event.getCode() != 0:
    print("Benchmark failed with bad exit code.")
    print("Exit code {}".format(exit_event.getCode()))
    exit(1)

print("{} ms".format(m5.curTick()/1e9))
