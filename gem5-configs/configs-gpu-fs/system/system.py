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

import math

import ConfigParser
import m5

from m5.objects import *
from m5.util import convert
from fs_tools import *
from common import SimpleOpts
from ruby import Ruby

class MySystem(LinuxX86System):

    SimpleOpts.add_option("--no_host_parallel", default=False,
        action="store_true",
        help="Do NOT run gem5 on multiple host threads (kvm only)")

    SimpleOpts.add_option("--disk-image",
        default='/proj/radl_tools/fs/ubuntu-18.4.img',
        help="The boot disk image to mount (/dev/hda)")

   # SimpleOpts.add_option("--second-disk",
   #     default='/proj/radl_tools/fs/linux-bigswap2.img',
   #     help="The second disk image to mount (/dev/hdb)")

    SimpleOpts.add_option("--kernel",
        default='/proj/radl_tools/fs/vmlinux',
        help="Linux kernel to boot")

    def __init__(self, opts):
        super(MySystem, self).__init__()
        self._opts = opts

        # Override defaults from common options / check for problems
        self._opts.network = "garnet2.0"
        self._opts.cpu_clock = '4GHz'
        self._opts.ruby_clock = '2GHz'


        # Set up the clock domain and the voltage domain
        self.clk_domain = SrcClockDomain()
        self.clk_domain.clock = self._opts.cpu_clock
        self.clk_domain.voltage_domain = VoltageDomain()

        # Setup a single memory range for X86
        self.setupMemoryRange()

        # Setup all the system devices
        self.initFS()

        # Set the boot disk image and add a swap disk for large input size
        # benchmarks.
        #self.setDiskImages(opts.disk_image, opts.second_disk)
        self.setDiskImage(opts.disk_image)

        # Use our self built kernel with no ACPI and 9p support.
        self.kernel = opts.kernel

        # Options specified on the kernel command line
        boot_options = ['earlyprintk=ttyS0', 'console=ttyS0,9600',
                        'lpj=7999923', 'root=/dev/sda1',
                        'drm_kms_helper.fbdev_emulation=0']
        self.boot_osflags = ' '.join(boot_options)

        # Create the CPUs for our system.
        self.createCPU()

        # Create the GPU
        if self._opts.dgpu or self._opts.apu:
            self.createGPU()

        # Create the memory heirarchy for the system.
        self.createMemoryHierarchy()

        # Set up the interrupt controllers for the system (x86 specific)
        self.setupInterrupts()

    def setupMemoryRange(self):
        mem_size = self._opts.mem_size
        excess_mem_size = \
                convert.toMemorySize(mem_size) - convert.toMemorySize('3GB')
        if excess_mem_size <= 0:
            self.mem_ranges = [AddrRange(0, size = mem_size)]
        else:
            print("Physical memory size specified is %s which is greater than"\
                  " 3GB.  Twice the number of memory controllers would be "\
                  "created."  % (mem_size))

            self.mem_ranges = [AddrRange(0, size = Addr('3GB')),
                        AddrRange(Addr('4GB'), size = excess_mem_size)]

        if self._opts.dgpu or self._opts.apu:
            self.shadow_rom_ranges = [AddrRange(0xc0000, size = Addr('128kB'))]

    def createGPU(self):
        # shader is the GPU
        self.shader = Shader(n_wf = self._opts.wfs_per_simd,
                        clk_domain = SrcClockDomain(
                        clock = self._opts.gpu_clock,
                            voltage_domain = VoltageDomain(
                                voltage = self._opts.gpu_voltage)))

        # VIPER GPU protocol implements release consistency at GPU side. So,
        # we make their writes visible to the global memory and should read
        # from global memory during kernal boundary. The pipeline initiates
        # (or do not initiate) the acquire/release operation depending on
        # these impl_kern_launch_rel and impl_kern_end_rel flags. The flag=true
        # means pipeline initiates a acquire/release operation at kernel
        # launch/end. VIPER protocol is write-through based, and thus only
        # impl_kern_launch_acq needs to set.
        if (buildEnv['PROTOCOL'] == 'GPU_VIPER'):
            self.shader.impl_kern_launch_acq = True
            self.shader.impl_kern_end_rel = False
        else:
            self.shader.impl_kern_launch_acq = True
            self.shader.impl_kern_end_rel = True

        # List of compute units; one GPU can have multiple compute units
        compute_units = []

        for i in xrange(self._opts.num_compute_units):
            compute_units.append(
                     ComputeUnit(cu_id = i, perLaneTLB = False,
                                 num_SIMDs = self._opts.simds_per_cu,
                                 wf_size = self._opts.wf_size,
                                 spbypass_pipe_length = \
                                 self._opts.sp_bypass_path_length,
                                 dpbypass_pipe_length = \
                                 self._opts.dp_bypass_path_length,
                                 issue_period = self._opts.issue_period,
                                 coalescer_to_vrf_bus_width = \
                                 self._opts.glbmem_rd_bus_width,
                                 vrf_to_coalescer_bus_width = \
                                 self._opts.glbmem_wr_bus_width,
                                 num_global_mem_pipes = \
                                 self._opts.glb_mem_pipes_per_cu,
                                 num_shared_mem_pipes = \
                                 self._opts.shr_mem_pipes_per_cu,
                                 n_wf = self._opts.wfs_per_simd,
                                 execPolicy = self._opts.CUExecPolicy,
                                 debugSegFault = self._opts.SegFaultDebug,
                                 functionalTLB = self._opts.FunctionalTLB,
                                 localMemBarrier = self._opts.LocalMemBarrier,
                                 countPages = self._opts.countPages,
                                 localDataStore = \
                                 LdsState(banks = self._opts.numLdsBanks,
                                          bankConflictPenalty = \
                                          self._opts.ldsBankConflictPenalty)))

            wavefronts = []
            vrfs = []
            vrf_pool_mgrs = []
            srfs = []
            srf_pool_mgrs = []
            for j in xrange(self._opts.simds_per_cu):
                for k in xrange(self.shader.n_wf):
                    wavefronts.append(Wavefront(simdId = j, wf_slot_id = k,
                                                wf_size = self._opts.wf_size))
                vrf_pool_mgrs.append(
                                 SimplePoolManager(pool_size = \
                                                   self._opts.vreg_file_size,
                                                   min_alloc = \
                                                   self._opts.vreg_min_alloc))

                vrfs.append(
                     VectorRegisterFile(simd_id=j, wf_size=self._opts.wf_size,
                                        num_regs=self._opts.vreg_file_size))

                srf_pool_mgrs.append(
                                 SimplePoolManager(pool_size = \
                                                   self._opts.sreg_file_size,
                                                   min_alloc = \
                                                   self._opts.vreg_min_alloc))
                srfs.append(
                    ScalarRegisterFile(simd_id=j, wf_size=self._opts.wf_size,
                                       num_regs=self._opts.sreg_file_size))

            compute_units[-1].wavefronts = wavefronts
            compute_units[-1].vector_register_file = vrfs
            compute_units[-1].scalar_register_file = srfs
            compute_units[-1].register_manager = \
                RegisterManager(policy=self._opts.registerManagerPolicy,
                                vrf_pool_managers=vrf_pool_mgrs,
                                srf_pool_managers=srf_pool_mgrs)
            if self._opts.TLB_prefetch:
                compute_units[-1].prefetch_depth = self._opts.TLB_prefetch
                compute_units[-1].prefetch_prev_type = self._opts.pf_type

            # attach the LDS and the CU to the bus (actually a Bridge)
            compute_units[-1].ldsPort = compute_units[-1].ldsBus.slave
            compute_units[-1].ldsBus.master = \
                compute_units[-1].localDataStore.cuPort


        self.shader.CUs = compute_units

        self.shader.cpu_pointer = self.cpu[0]

    # Creates TimingSimpleCPU by default
    def createCPU(self):
        self.warmupCpu = [TimingSimpleCPU(cpu_id = i, switched_out = True)
                          for i in range(self._opts.num_cpus)]
        map(lambda c: c.createThreads(), self.warmupCpu)
        if self._opts.cpu_type == "TimingSimpleCPU":
            print("Running with Timing Simple CPU")
            self.mem_mode = 'timing'
            self.cpu = [TimingSimpleCPU(cpu_id = i, switched_out = False)
                              for i in range(self._opts.num_cpus)]
            map(lambda c: c.createThreads(), self.cpu)
        elif self._opts.cpu_type == "AtomicSimpleCPU":
            print("Running with Atomic Simple CPU")
            if self._opts.ruby:
                self.mem_mode = 'atomic_noncaching'
            else:
                self.mem_mode = 'atomic'
            self.cpu = [AtomicSimpleCPU(cpu_id = i, switched_out = False)
                              for i in range(self._opts.num_cpus)]
            map(lambda c: c.createThreads(), self.cpu)
        elif self._opts.cpu_type == "DerivO3CPU":
            print("Running with O3 CPU")
            self.mem_mode = 'timing'
            self.cpu = [DerivO3CPU(cpu_id = i, switched_out = False)
                              for i in range(self._opts.num_cpus)]
            map(lambda c: c.createThreads(), self.cpu)
        elif self._opts.cpu_type == "X86KvmCPU":
            print("Running with KVM to start")
            # Note KVM needs a VM and atomic_noncaching
            self.mem_mode = 'atomic_noncaching'
            self.cpu = [X86KvmCPU(cpu_id = i, hostFreq = "3.6GHz")
                        for i in range(self._opts.num_cpus)]
            self.kvm_vm = KvmVM()
            map(lambda c: c.createThreads(), self.cpu)
        else:
            panic("Bad CPU type!")

    def switchCpus(self, old, new):
        assert(new[0].switchedOut())
        m5.switchCpus(self, zip(old, new))

    def setDiskImages(self, img_path_1, img_path_2):
        disk0 = CowDisk(img_path_1)
        disk2 = CowDisk(img_path_2)
        self.pc.south_bridge.ide.disks = [disk0, disk2]

    def setDiskImage(self, img_path_1):
        disk0 = CowDisk(img_path_1)
        self.pc.south_bridge.ide.disks = [disk0]

    def createDMADevices(self):
        if self._opts.dgpu or self._opts.apu:
            # Set up the HSA packet processor
            hsapp_gpu_map_paddr = int(Addr(self._opts.mem_size))
            gpu_hsapp = HSAPacketProcessor(pioAddr=hsapp_gpu_map_paddr,
                                          numHWQueues=self._opts.num_hw_queues)

            dispatcher = GPUDispatcher()
            gpu_cmd_proc = GPUCommandProcessor(hsapp=gpu_hsapp,
                                               dispatcher=dispatcher)

            self.shader.dispatcher = dispatcher
            self.shader.gpu_cmd_proc = gpu_cmd_proc
            self._dma_ports.append(gpu_hsapp)
            self._dma_ports.append(gpu_cmd_proc)

    def createMemoryHierarchy(self):
        self.createDMADevices()

        # VIPER requires the number of instruction and scalar caches
        if (buildEnv['PROTOCOL'] == 'GPU_VIPER'):
            # Currently, the sqc (I-Cache of GPU) is shared by
            # multiple compute units(CUs). The protocol works just fine
            # even if sqc is not shared. Overriding this option here
            # so that the user need not explicitly set this (assuming
            # sharing sqc is the common usage)
            self._opts.num_sqc = \
                int(math.ceil(float(self._opts.num_compute_units)\
                                    / self._opts.cu_per_sqc))
            self._opts.num_scalar_cache = \
                int(math.ceil(float(self._opts.num_compute_units)\
                                        / self._opts.cu_per_scalar_cache))

        Ruby.create_system(self._opts, True, self, self.iobus,
                           self._dma_ports, None)

        # don't connect ide as it gets connected in attachIO call
        for dma_port in self._dma_ports[1:]:
            dma_port.pio = self.iobus.master

        self.ruby.clk_domain = SrcClockDomain()
        self.ruby.clk_domain.clock = self._opts.ruby_clock
        self.ruby.clk_domain.voltage_domain = VoltageDomain()

        for i, cpu in enumerate(self.cpu):
            cpu.icache_port = self.ruby._cpu_ports[i].slave
            cpu.dcache_port = self.ruby._cpu_ports[i].slave

            cpu.itb.walker.port = self.ruby._cpu_ports[i].slave
            cpu.dtb.walker.port = self.ruby._cpu_ports[i].slave


        if self._opts.dgpu or self._opts.apu:
            gpu_port_idx = len(self.ruby._cpu_ports) \
                           - self._opts.num_compute_units \
                           - self._opts.num_sqc \
                           - self._opts.num_scalar_cache

            for i in xrange(self._opts.num_compute_units):
                for j in xrange(self._opts.wf_size):
                    self.shader.CUs[i].memory_port[j] = \
                        self.ruby._cpu_ports[gpu_port_idx].slave[j]
                gpu_port_idx += 1

            for i in xrange(self._opts.num_compute_units):
                if i > 0 and not i % self._opts.cu_per_sqc:
                    gpu_port_idx += 1
                self.shader.CUs[i].sqc_port = \
                    self.ruby._cpu_ports[gpu_port_idx].slave

            gpu_port_idx += 1

            for i in xrange(self._opts.num_compute_units):
                if i > 0 and not i % self._opts.cu_per_scalar_cache:
                    gpu_port_idx += 1
                self.shader.CUs[i].scalar_port = \
                    self.ruby._cpu_ports[gpu_port_idx].slave

    def setupInterrupts(self):
        for i, cpu in enumerate(self.cpu):
            # create the interrupt controller CPU and connect to RubyPort
            cpu.createInterruptController()

            # For x86 only, connect interrupts to the memory
            # Note: these are directly connected to RubyPort and
            #       not cached
            cpu.interrupts[0].pio = self.ruby._cpu_ports[i].master
            cpu.interrupts[0].int_master = self.ruby._cpu_ports[i].slave
            cpu.interrupts[0].int_slave = self.ruby._cpu_ports[i].master

    def initFS(self):
        self.pc = Pc()

        # North Bridge
        self.iobus = IOXBar()

        # add the ide to the list of dma devices that later need to attach to
        # dma controllers
        if (buildEnv['PROTOCOL'] == 'GPU_VIPER'):
            # VIPER expects the port itself while others use the dma object
            self._dma_ports = [self.pc.south_bridge.ide]
            self.pc.attachIO(self.iobus, [p.dma for p in self._dma_ports])
        else:
            self._dma_ports = [self.pc.south_bridge.ide.dma]
            self.pc.attachIO(self.iobus, [port for port in self._dma_ports])

        if self._opts.dgpu or self._opts.apu:
            # add GPU to southbridge
            self.pc.south_bridge.attachGPU(self.iobus,
                             [port.dma for port in self._dma_ports])

        self.intrctrl = IntrControl()

        ###############################################

        # Add in a Bios information structure.
        self.smbios_table.structures = [X86SMBiosBiosInformation()]

        # Set up the Intel MP table
        base_entries = []
        ext_entries = []

        for i in range(self._opts.num_cpus):
            bp = X86IntelMPProcessor(
                    local_apic_id = i,
                    local_apic_version = 0x14,
                    enable = True,
                    bootstrap = (i ==0))
            base_entries.append(bp)

        io_apic = X86IntelMPIOAPIC(
                id = self._opts.num_cpus,
                version = 0x11,
                enable = True,
                address = 0xfec00000)
        self.pc.south_bridge.io_apic.apic_id = io_apic.id
        base_entries.append(io_apic)

        pci_bus = X86IntelMPBus(bus_id = 0, bus_type='PCI   ')
        base_entries.append(pci_bus)
        isa_bus = X86IntelMPBus(bus_id = 1, bus_type='ISA   ')
        base_entries.append(isa_bus)
        connect_busses = X86IntelMPBusHierarchy(bus_id=1,
                subtractive_decode=True, parent_bus=0)
        ext_entries.append(connect_busses)
        pci_dev4_inta = X86IntelMPIOIntAssignment(
                interrupt_type = 'INT',
                polarity = 'ConformPolarity',
                trigger = 'ConformTrigger',
                source_bus_id = 0,
                source_bus_irq = 0 + (4 << 2),
                dest_io_apic_id = io_apic.id,
                dest_io_apic_intin = 16)
        base_entries.append(pci_dev4_inta)

        def assignISAInt(irq, apicPin):
            assign_8259_to_apic = X86IntelMPIOIntAssignment(
                    interrupt_type = 'ExtInt',
                    polarity = 'ConformPolarity',
                    trigger = 'ConformTrigger',
                    source_bus_id = 1,
                    source_bus_irq = irq,
                    dest_io_apic_id = io_apic.id,
                    dest_io_apic_intin = 0)
            base_entries.append(assign_8259_to_apic)
            assign_to_apic = X86IntelMPIOIntAssignment(
                    interrupt_type = 'INT',
                    polarity = 'ConformPolarity',
                    trigger = 'ConformTrigger',
                    source_bus_id = 1,
                    source_bus_irq = irq,
                    dest_io_apic_id = io_apic.id,
                    dest_io_apic_intin = apicPin)
            base_entries.append(assign_to_apic)

        assignISAInt(0, 2)
        assignISAInt(1, 1)
        for i in range(3, 15):
            assignISAInt(i, i)
        self.intel_mp_table.base_entries = base_entries
        self.intel_mp_table.ext_entries = ext_entries

        entries = \
           [
            # Mark the first megabyte of memory as reserved
            X86E820Entry(addr = 0, size = '639kB', range_type = 1),
            X86E820Entry(addr = 0x9fc00, size = '385kB', range_type = 2),
            # Mark the rest of physical memory as available
            X86E820Entry(addr = 0x100000,
                    size = '%dB' % (self.mem_ranges[0].size() - 0x100000),
                    range_type = 1),
            ]
        # Mark [mem_size, 3GB) as reserved if memory less than 3GB, which
        # force IO devices to be mapped to [0xC0000000, 0xFFFF0000). Requests
        # to this specific range can pass though bridge to iobus.
        entries.append(X86E820Entry(addr = self.mem_ranges[0].size(),
            size='%dB' % (0xC0000000 - self.mem_ranges[0].size()),
            range_type=2))

        # Reserve the last 16kB of the 32-bit address space for m5ops
        entries.append(X86E820Entry(addr = 0xFFFF0000, size = '64kB',
                                    range_type=2))

        # Add the rest of memory. This is where all the actual data is
        entries.append(X86E820Entry(addr = self.mem_ranges[-1].start,
            size='%dB' % (self.mem_ranges[-1].size()),
            range_type=1))

        self.e820_table.entries = entries
