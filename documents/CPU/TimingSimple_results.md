## **Timing Simple CPU:**

### Execution benchmarks:

- EI  : 8 Independent Instructions
- EF  : 16 Independent Instructions
- ED1 : 1 Dependency Chain per instruction
- EM1 : 1 dependency chain with multiplies
- EM5 : 5 dependency chain with multiplies

### Memory Latency:

- Perfect : Perfect memory, it takes ‘0ns’ for any memory access.
- SingleCycle : It takes '1ns' for any memory access.

### Simple_Timing CPU

The TimingSimpleCPU is the version of SimpleCPU that uses timing memory accesses. It has a 2 stage pipeline, (Fetch + Execute).
The timing simple advances to "next fetch" in the same cycle as the "execute" stage.


![TimingSimpleCPU](images/TimingSimpleCPU.png)


**The Timing Simple with perfect** 

Since execute and next-fetch happens at the same time, without memory latency (perfect memory), it takes only the initial latency for fetch and every execution happens at zero time and the entire benchmark executes in 1 or 2 cycles, which gives a very high IPC.

![IPC_PERFECT_SIMPLE](images/IPC_execbenchmarks_Perfect_simple.png)


**The Timing Simple in Single cycle**

Since this is an execution benchmark suite with only arithmetic independent instruction, the latency we see is mostly because of fetch.

In single-Cycle memory bandwidth, the memory access to fetch takes 1 cycle and hence the IPC largely dependents on the number of instruction fetches made.

![IPC_SINGLECYCLE_SIMPLE](images/IPC_SINGLECYCLE_SIMPLE.png)


**Conclusion**

[TimingSimple](http://www.gem5.org/documentation/general_docs/cpu_models/SimpleCPU) is an in-order 2 stage simple CPU, and could be useful to measure the memory latency involved in benchmarks.









