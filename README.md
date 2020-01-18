# gem5art-experiments
gem5art experiments to run microbenchmark:

The repo has 2 launch scripts:
1.  [launch_microbenchmark.py](launch_micorbenchmark).
    It is used to run simple microbenchmark experiments.
2.  [launch_microbenc_allconfigs.py](launch_microbench_allconfigs.py)
    This launchscript lets you set various basic configuration for running micorbenchmark experiments.

## Launch_microbench_allconfigs

There are 3 main configuration which can be run using this launchscript.
- General Configuration : 
This is a basic configuration to run all benchmarks for all specified CPU for a fixed branchpredictor.

    In the script , set:
        
    ```python
    config = config1
    ```

- Different Branch Predictors:
This is a configuration to run all benchmarks for a CPU using different branch predictors.

    In the script , set:

    ```python
    config = config2

    cpu_bp = 'Simple' #(cpu of your choice)
    ```
- Difefrent cache size.
This is a  configuration to run experiments with different L1 cache size with L2 size fixed or  different L2 cache size with L1 size fixed
   
    In the script , set:

    ```python
    config = config3

    cache_type = 'L1_cache' #'L2_cache'
    #L1Cache_sizes.
    L1D = ['4kB','32kB','64kB']
    #L2Cache_sizes.
    L2C = ['512kB','1MB']

    ```

All these configuration can also be run for various other ISA.
   
   In the script , set:
   ```python
    arch = 'X86' #(ARM)
```




   
        


