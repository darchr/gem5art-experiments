## Running Microbenchmarks
 There are two launch scripts to micro-benchmarks.

- [launch_microbenchmarks.py](launch_microbenchmark.py)
: Launch script to run basic microbenchmark experiment for all cpu.

- [launch_microbench_allconfig.py](launch_microbench_allconfig.py)
: Launch script to run microbenchmarks with different configuration.

### launch_microbench_allconfig.py

There are many different experiments which can be run using this launch script with the help of various command_line parameters.

Use  the below Option to select the configuration you want to run:

 --config [config_base, config_control, config_memory]

- Config_base:
   
   To run basic microbenchmark experiment for all cpu.

    | Options   | Choices                          | Default |
    |-----------|----------------------------------|---------|
    | --bm_list | control, memory, main_memory,all | all     |
    |           |                                  |         |

- config_control:
     
    To run microbenchmark experiments using different branch preidctors for selected CPU.

    | Options   | Choices                           | Default |
    |-----------|-----------------------------------|---------|
    | --bm_list | control, memory, main_memory, all | all     |
    | --cpu     | simple, O3                        | simple  |

- config_memory:

    To run microbenchmark experiments for all cpu with different L1 or L2 cache size.

    | options      | choices                           | default  |
    |--------------|-----------------------------------|----------|
    | --bm_list    | control, memory, main_memory, all | all      |
    | --cache_type | L1_cache, L2_cache                | L1_cache |



