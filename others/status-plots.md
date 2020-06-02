# Boot Tests

# NPB Tests

These NPB tests use KVM CPU (1,8,16,32, and 64 cores) and TimingSimple CPU (1 and 8 cores) with MESI_Two_Level memory system.

![NPB Status with KVM CPU](status-plots/npb_multicore_kvm.png)

It is a known problem that if the number of simulated CPU cores increase, KVM simulations get stuck sometimes.
A work around is to use lower number of event queues than the CPU cores.
Although our scripts do that for more than 1 CPU core, the cases shown as `timeout` in the plot above
suffer from this problem of getting stuck.

![NPB Status with TimingSimple CPU](status-plots/npb_multicore_timing.png)

There are three cases with TimingSimple CPU which did not finish in the alloted time.
There is no reason apparent in the generated results files (`simout`, `simerr`, `system.pc.com_1.device`).

# PARSEC Tests

# GAPBS Tests

# SPEC 2006 Tests

The following plot represent the status of SPEC2006 workloads for different CPUs and data sizes with respect to gem5-20, linux kernel version 4.19.83 and gcc version 7.5.0.

![SPEC-2006 status fro gem5-20 ](status-plots/spec2006_gem5-20_status.png)

* Few workloads, [**400.perlbench**, **447.dealII**, **450.soplex**, **483.xalancbmk**] had build errors
* **434.zeusmp** had crashed in gem5-19 as well due a segmentation fault.
* **453.povray** needs a rerun and the test with gem5-19 was a success. 

# SPEC 2017 Tests

The following plot represent the status of SPEC2017 workloads with respect to gem5-20, linux kernel version 4.19.83 and gcc version 7.5.0.

![SPEC-2017 status fro gem5-20 ](status-plots/spec2017_gem5-20_status.png)

* **600.perlbench_s** kernel panic while booting, couldn't find a reason.