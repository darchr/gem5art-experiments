#!/usr/bin/env python3

from pymongo import MongoClient
from uuid import UUID
import json

db = MongoClient().artifact_database


'''
This script reads the gem5 run objects
created by boot tests and creates a list
of runs that were successful

Output list consists of strings of the format:
[cpu-model]_[linux-version]_[boot-type]_[mem-model]_[cpu-count]

For now this script is reading run objects from
the stored files on the file system.
Later, it will be updated to get this information from
the database

Anyone interested in finding out the status of linux
boot tests for their runs, should be able to
tokenize the elements of the list to get the
working configuration (cpu model, linux version etc.)
'''


def working_status(linux, cpu, mem, num_cpum, boot_type):
    with open('/fasthome/aakahlow/boot_tests/results/run_exit/vmlinux-{}/boot-exit/{}/{}/{}/{}/info.json'.format(linux, cpu, mem, num_cpu, boot_type)) as f:
        data = json.load(f)
        if(data['status'] == 'Finished'):
            return True


if __name__ == "__main__":

    linuxes = ['5.2.3', '4.19.83', '4.14.134', '4.9.186', '4.4.186']
    boot_types = ['init', 'systemd']
    cpu_types = ['kvm', 'atomic', 'simple', 'o3']
    num_cpus = ['1', '2', '4', '8']
    mem_types = ['classic', 'ruby']


    working_list = []

    for linux in linuxes:
        for boot_type in boot_types:
            for cpu in cpu_types:
                for num_cpu in num_cpus:
                    for mem in mem_types:
                        if working_status(linux, cpu, mem, num_cpu, boot_type):
                            working_list.append('{}_{}_{}_{}_{}'.format(cpu,linux,boot_type,mem,num_cpu))