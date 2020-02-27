#!/bin/sh

# This file is the script that runs on the gem5 guest. This reads a file from the host via m5 readfile
# which contains the workload if it's synthetic or real graph and the size to run.

cd /home/gem5/gapbs

# Read workload file
m5 readfile > workloadfile.sh
echo "Done reading workloads"

# The workload file should always exists
echo "Workload detected"


# Read the name of the workload, the size of the workload
read -r workload arg size < workloadfile
./$workload $arg $size;
m5 exit