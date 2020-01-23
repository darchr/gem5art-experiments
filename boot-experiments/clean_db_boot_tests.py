#!/usr/bin/env python3

from pymongo import MongoClient
from uuid import UUID

db = MongoClient().artifact_database


'''
This file updates the run object entries in the database,
so that the all (and only) valid runs have a name field
'name' = 'boot_tests_timeout'
'''

# Updating boot tests run objects with classic memory system

linuxes = ['5.2.3', '4.19.83', '4.14.134', '4.9.186', '4.4.186']
boot_types = ['init', 'systemd']
cpu_types = ['kvm', 'atomic', 'simple', 'o3']
num_cpus = ['1', '2', '4', '8']
mem_types = ['classic']

name_exists = 0

for linux in linuxes:
    for boot_type in boot_types:
        for cpu in cpu_types:
            for num_cpu in num_cpus:
                for mem in mem_types:
                    name_exists = 0
                    for i in db.artifacts.find({'outdir':'/fasthome/aakahlow/boot_tests/results/run_exit/vmlinux-{}/boot-exit/{}/{}/{}/{}'.format(linux, cpu, mem, num_cpu, boot_type)}):
                        if 'name' in i.keys():
                            name_exists = 1
                    # if the run object does not have a name field, add it
                    # Only add it to the latest run object, in case multiple run objects are found based
                    # on the above filter
                    print(name_exists)
                    if name_exists == 0:
                        i_old = i.copy()
                        i['name'] = 'boot_tests_timeout'
                        db.artifacts.replace_one(i_old, i, True)




# Updating boot tests run objects with ruby memory system

mem_types = ['ruby']

for linux in linuxes:
    for boot_type in boot_types:
        for cpu in cpu_types:
            for num_cpu in num_cpus:
                for mem in mem_types:
                    for i in db.artifacts.find({'outdir':'/fasthome/aakahlow/boot_tests/results/run_exit/vmlinux-{}/boot-exit/{}/{}/{}/{}'.format(linux, cpu, mem, num_cpu, boot_type)}):
                        #only the ruby runs with these config scripts are valid
                        if i['run_script'] == 'configs-boot-tests-temp/run_exit.py':
                            i_old = i.copy()
                            i['name'] = 'boot_tests_timeout'
                            db.artifacts.replace_one(i_old, i, True)
                        else:
                            #these entries will already have name entry, but are invalid
                            i_old = i.copy()
                            i['name'] = 'boot_tests_timeout_invalid'
                            db.artifacts.replace_one(i_old, i, True)



