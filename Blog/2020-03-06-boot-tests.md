---
layout: post
title:  "Linux Boot Tests on gem5-19"
author: Ayaz Akram
date:   2020-03-06
categories: project
---

# Linux Boot Tests on gem5-19
The frequency of changes pushed to gem5 is increasing with time.
This makes it important to have an update to date idea of what is working with gem5 and what is not.
Booting of linux kernel is a very important benchmark to ascertain the working status of gem5, considering that
gem5 is a full-system simulator.
State of support of latest linux kernel versions on gem5 is not known.
Also, previously available linux kernels or configuration files on gem5 website are quite old.
[gem5-19](https://www.gem5.org/project/2020/02/25/gem5-19.html) has recently been released.
So, we ran few tests to discover where does gem5-19 stand in terms of its ability to boot linux, specially for newer linux kernel versions.
In this post, we will have a look at the results of these tests.

## Configuration Space
The possible configuration space (linux kernel versions, memory systems, cpu models, linux boot type, core count) when it comes to simulating linux boot on gem5 is large.
For these tests, we used four latest LTS (long term support) linux kernels (v4.4.186, v4.9.186, v4.14.134, v4.19.83) and a recent stable kernel (v5.2.3) with all possible configurations along the dimensions of memory systems (classic, ruby), cpu models (kvm, atomic, simple, o3), linux boot type (with only init script, with systemd) and core count (1,2,4,8).

## gem5art
We used [gem5art](https://gem5art.readthedocs.io/en/latest/index.html) (library for artifacts, reproducibility, and testing) to perform these experiments.
gem5art helps to conduct gem5 experiments in a more structured and reproducible way.
We will defer the detailed discussion on gem5art for a future blog post.
The gem5 configuration scripts used to run these experiments are available [here](https://github.com/darchr/gem5art/tree/master/docs/gem5-configs/configs-boot-tests/) and the details of how these experiments were run using gem5art can be found [here](https://gem5art.readthedocs.io/en/latest/tutorials/boot-tutorial.html).
The built disk image and linux kernel binaries are also available from the following links: ([disk image](http://dist.gem5.org/images/x86/ubuntu-18-04/base.img), [vmlinux-4.14.134](http://dist.gem5.org/kernels/x86/static/vmlinux-4.14.134), [vmlinux-4.14.134](http://dist.gem5.org/kernels/x86/static/vmlinux-4.14.134), [vmlinux-4.19.83](http://dist.gem5.org/kernels/x86/static/vmlinux-4.19.83), [vmlinux-4.4.186](http://dist.gem5.org/kernels/x86/static/vmlinux-4.4.189), [vmlinux-5.2.3](http://dist.gem5.org/kernels/x86/static/vmlinux-5.2.3), and [vmlinux-4.9.186](http://dist.gem5.org/kernels/x86/static/vmlinux-4.9.186)).


## Linux Booting Status
Figure 1 and 2 show the results of these experiments with classic memory system for init and systemd boot type respectively.
Figure 3 and 4 show the results of these experiments for ruby memory system for init and systemd boot type respectively.
All possible status outputs (shown in the figures below) are defined as follows:

- **timeout:** experiment did not finish in a reasonable amount of time (8 hours: this time is used considering that the similar successful cases do not take longer than this on the used host machine).
- **not-supported:** cases which are not yet supported in gem5.
- **success:** cases where linux booted successfully.
- **sim-crash:** cases where gem5 crashed.
- **kernel-panic:** cases where kernel went into panic during simulation.

For classic memory system, KVM and Atomic cpu models seem to work always.
TimingSimple cpu always work for a single core, but fails to boot linux kernel for multiple cpu cores.
O3 cpu model fails to simulate linux booting in most of the cases (only success is init boot type with two linux kernel versions).

![](boot_classic_init)
<br>
*Figure 1: Linux boot status for classic memory system and init boot*


![](boot_classic_systemd)
<br>
*Figure 2: Linux boot status for classic memory system and systemd boot*


As shown in Figure 3 and 4, for Ruby memory system, KVM and Atomic cpu models seem to work except a couple of cases where even KVM cpu model times out.
TimingSimple cpu works upto 2 cores, but fails for 4 and 8 cores.
O3 cpu model fails to simulate linux booting or times out in all of the cases.

![](boot_ruby_init)
<br>
*Figure 3: Linux boot status for ruby memory system and init boot*

![](boot_ruby_systemd)
<br>
*Figure 4: Linux boot status for ruby memory system and systemd boot*

## Things to do Moving Forward
Researchers mostly fast-forward simulation during linux boot to avoid the problems seen above or end up using older kernel versions.
This leads to uncertainty in simulation results and conclusions drawn from such experiments.
As a community, we should not overlook these problems and try to enable gem5 to successfully run these boot tests.
There are few JIRA issues
([GEM5-359](https://gem5.atlassian.net/projects/GEM5/issues/GEM5-359?filter=reportedbyme&orderby=created%20DESC), [GEM5-360](https://gem5.atlassian.net/projects/GEM5/issues/GEM5-360?filter=reportedbyme&orderby=created%20DESC))
opened on gem5 JIRA to document these problems and eventually fix them.

Secondly, we need to keep repeating these tests continuously to ensure that new changes do not break gem5's ability to simulate linux booting.
We also need to keep updating these tests as new linux kernel versions are released.
We plan to keep on updating the gem5 website with the status of these boot tests regularly with new gem5 releases.