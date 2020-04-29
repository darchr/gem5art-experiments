# gem5art-experiments

This repository contains different files (launch scripts, gem5 configuration files, disk image and linux configuration files) needed to run experiments with gem5art.
This README describes how to run different experiments with gem5art step-by-step and points to the detailed documentation on these experiments as well.


**Note:** The user should make sure to create a local git repository containing all files for a particular experiment (which can be accessed from this repository), and add a remote to that repository as well.

The commands to do this:

```
git init
git remote add origin https://your-remote-add/[any]-experiments.git
```

## Steps to Run Full System Linux Boot Tests

First, you have to download all the required files needed to run these experiments from this repo.
The required files are as follows:

- [gem5 configurations for boot tests](gem5-configs/configs-boot-tests)
- [disk image files specific for boot tests](disk-images/boot-exit)
- [disk image files shared among all experiments](disk-images/shared)
- [launch script for boot tests](launch-scripts/launch_boot_tests.py)
- [Linux kernel configuration files](linux-configs/)
- [.gitignore file](.gitignore)

In case of confusion on the directory structure to keep these files, refer to the gem5art boot tests [tutorial](https://gem5art.readthedocs.io/en/latest/tutorials/boot-tutorial.html).

Once, you have downloaded all these files, follow the following steps to run full system linux boot tests:

To create python3 virtual environment:

```sh
virtualenv -p python3 venv
source venv/bin/activate
```

To install gem5art if not already installed:
```sh
pip install gem5art-artifact gem5art-run gem5art-tasks
```

To build gem5:
```sh
git clone https://gem5.googlesource.com/public/gem5
git checkout d40f0bc579fb8b10da7181
cd gem5
scons build/X86/gem5.opt -j8
```

To build m5 util:
```sh
cd gem5/util/m5/
make -f Makefile.x86
```

To create a disk image:
```sh
cd disk-image/
wget https://releases.hashicorp.com/packer/1.4.3/packer_1.4.3_linux_amd64.zip
unzip packer_1.4.3_linux_amd64.zip
./packer validate boot-exit/boot-exit.json
./packer build boot-exit/boot-exit.json
```

To compile the linux kernel:
```sh
git clone https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
mv linux linux-stable
cd linux-stable
git checkout v{version-no: e.g. 5.2.3}
cp ../linux-configs/config.{version-no: e.g. 5.2.3} .config
make -j8
cp vmlinux vmlinux-{version-no: e.g. 5.2.3}
```
Repeat the above compiling commands for other four linux versions (v4.19.83, v4.14.134, v4.9.186, v4.4.186).

Run the database (if not already running) using (run this command after creating a directory):

```sh
docker run -p 27017:27017 -v <absolute path to the created directory>:/data/db --name mongo-<some tag> -d mongo
```

Run a celery server using (unless this experiment is run by someone in DArchR):

```sh
celery -E -A gem5art.tasks.celery worker --autoscale=[number of workers],0
```

For users inside DArchR follow these [steps](#using-shared-celery-server), to run your experiments using centralized celery server.

Finally, run the [launch script](launch-scripts/launch_boot_tests.py) to start running these experiments:

```sh
python launch_boot_tests.py
```

Details of these experiments can be seen in a tutorial [here](https://gem5art.readthedocs.io/en/latest/tutorials/boot-tutorial.html).

Results of these experiments are available [here](results/boot-experiments/boot_tests_gem5art.ipynb)

## Steps to Run NAS Parallel Benchmarks

As in boot tests, you will have to download all the required files needed to run these experiments from this gem5art-experiments repo.

The required files are as follows:

- [gem5 configurations for npb tests](gem5-configs/configs-npb-tests)
- [disk image files specific for npb tests](disk-images/npb)
- [disk image files shared among all experiments](disk-images/shared)
- [launch script for npb tests](launch-scripts/launch_npb_tests.py)
- [Linux kernel configuration file for kernel 4.19.83](linux-configs/config.4.19.83)
- [.gitignore file](.gitignore)

In case of confusion on the directory structure to keep these files, refer to the gem5art npb tests [tutorial](https://gem5art.readthedocs.io/en/latest/tutorials/npb-tutorial.html).

Once, you have downloaded all the required files from this repo, follow the following steps to run these experiments:

To create python3 virtual environment:

```sh
virtualenv -p python3 venv
source venv/bin/activate
```

To install gem5art if not already installed:
```sh
pip install gem5art-artifact gem5art-run gem5art-tasks
```

To build gem5:
```sh
git clone https://gem5.googlesource.com/public/gem5
cd gem5
git checkout d40f0bc579fb8b10da7181
git remote add darchr https://github.com/darchr/gem5
git fetch darchr
git cherry-pick 6450aaa7ca9e3040fb9eecf69c51a01884ac370c
git cherry-pick 3403665994b55f664f4edfc9074650aaa7ddcd2c
scons build/X86/gem5.opt -j8
```

To build m5 util:
```sh
cd gem5/util/m5/
make -f Makefile.x86
```

To create a disk image:
```sh
cd disk-image/
wget https://releases.hashicorp.com/packer/1.4.3/packer_1.4.3_linux_amd64.zip
unzip packer_1.4.3_linux_amd64.zip

cd npb
git clone https://github.com/darchr/npb-hooks.git

cd ..

./packer validate npb/npb.json
./packer build npb/npb.json
```

To compile the linux kernel:
```sh
git clone --branch v4.19.83 --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
mv linux linux-stable
cd linux-stable
cp ../config.4.19.83 .config
make -j8
cp vmlinux vmlinux-4.19.83
```

Run the database (if not already running) using (run this command after creating a directory):

```sh
docker run -p 27017:27017 -v <absolute path to the created directory>:/data/db --name mongo-<some tag> -d mongo
```

Run a celery server using (unless this experiment is run by someone in DArchR):

```sh
celery -E -A gem5art.tasks.celery worker --autoscale=[number of workers],0
```

For users inside DArchR follow these [steps](#using-shared-celery-server), to run your experiments using centralized celery server.

Finally, run the [launch script](launch-scripts/launch_npb_tests.py) to start running these experiments:

```sh
python launch_npb_tests.py
```

Details of these experiments can be seen in a tutorial [here](https://gem5art.readthedocs.io/en/latest/tutorials/npb-tutorial.html).

Results of these experiments are available [here](results/npb-experiments/npb_gem5art.ipynb).

## Steps to Run SPEC CPU 2006 / SPEC CPU 2017 Benchmarks

Suppose we place the experiment in gem5art-spec-experiment folder, which follows the folder structure as laid out in [gem5art-template](https://github.com/darchr/gem5art-template) repo.

The following are commands to re-create the experiment described [here](https://gem5art.readthedocs.io/en/latest/tutorials/spec2006-tutorial.html) and [here](https://gem5art.readthedocs.io/en/latest/tutorials/spec2017-tutorial.html).

To copy disk image scripts, gem5 run scripts, linux config files, and the launch scripts,
```sh
git clone https://github.com/darchr/gem5art-experiments
mkdir gem5art-spec-experiment
mkdir gem5art-spec-experiment/disk-image
mkdir gem5art-spec-experiment/gem5-configs
mkdir gem5art-spec-experiment/linux-configs
mkdir gem5art-spec-experiment/results
cp -r gem5art-experiments/disk-images/spec2006 gem5art-spec-experiment/disk-image/
cp -r gem5art-experiments/disk-images/spec2017 gem5art-spec-experiment/disk-image/
cp -r gem5art-experiments/disk-images/shared gem5art-spec-experiment/disk-image/
cp -r gem5art-experiments/gem5-configs/configs-spec-tests/* gem5art-spec-experiment/gem5-configs/
cp -r gem5art-experiments/linux-configs/config.4.19.83 gem5art-spec-experiment/linux-configs/
cp -r gem5art-experiments/launch-scripts/launch_spec2006_experiments.py gem5art-spec-experiment/
cp -r gem5art-experiments/launch-scripts/launch_spec2017_experiments.py gem5art-spec-experiment/
cp -r gem5art-experiments/.gitignore gem5art-spec-experiment/
```

To clone gem5 repo,
```sh
cd gem5art-spec-experiment
git clone https://gem5.googlesource.com/public/gem5
cd gem5
git remote add darchr https://github.com/darchr/gem5
git fetch darchr
git cherry-pick 6450aaa7ca9e3040fb9eecf69c51a01884ac370c
git cherry-pick 3403665994b55f664f4edfc9074650aaa7ddcd2c
cd ..
```

To build gem5,
```sh
cd gem5art-spec-experiment/gem5/
scons build/X86/gem5.opt -j $(nproc)
cd ..
```

To build m5,
```sh
cd gem5art-spec-experiment/gem5/util/m5/
make -f Makefile.x86
cd -
```

To clone linux repo,
```sh
cd gem5art-spec-experiment
git clone --branch v4.19.83 --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/
mv linux linux-4.19.83
cd ..
```

To build linux kernel,
```sh
cd gem5art-spec-experiment
cp linux-configs/config.4.19.83 linux-4.19.83/.config
cd linux-4.19.83
make -j $(nproc)
cp vmlinux vmlinux-4.19.83
cd ..
```

To build disk images,
```sh
cd disk-image/
wget https://releases.hashicorp.com/packer/1.4.5/packer_1.4.5_linux_amd64.zip
unzip packer_1.4.5_linux_amd64.zip
rm packer_1.4.5_linux_amd64.zip
./packer validate spec2006/spec2006.json
./packer build spec2006/spec2006.json
./packer validate spec2017/spec2017.json
./packer build spec2017/spec2017.json
```


## Steps to Run microbenchmark-experiments

The particular microbenchmarks we are using in this tutorial were originally developed at the University of Wisconsin-Madison. This microbenchmark suite is divided into different control, execution and memory benchmarks. We will use system emulation (SE) mode of gem5 to run these microbenchmarks with gem5.

To download the microbench source code:

```sh
git clone https://github.com/darchr/microbench.git
```
Commit the source of microbenchmarks to the micro-tests repo (so that the current version of microbenchmarks becomes a part of the micro-tests reposiotry).

```sh
git add microbench/
git commit -m "Add microbenchmarks"
```

compile the benchmarks:

```sh
cd microbench
make
```

To create python3 virtual environment:

```sh
virtualenv -p python3 venv
source venv/bin/activate
```

Run the database (if not already running) using (run this command after creating a directory):

```sh
docker run -p 27017:27017 -v <absolute path to the created directory>:/data/db --name mongo-<some tag> -d mongo
```

Run a celery server using (unless this experiment is run by someone in DArchR):

```sh
celery -E -A gem5art.tasks.celery worker --autoscale=[number of workers],0
```

(For users inside DArchR follow these [steps](#using-shared-celery-server) to run your experiments using centralized celery server.)


 There are two launch scripts to micro-benchmarks.

- [launch-scripts/launch_microbenchmarks.py](launch_microbenchmark.py)
: Launch script to run basic microbenchmark experiment for all cpu.

- [launch-scripts/launch_microbench_allconfig.py](launch_microbench_allconfig.py)
: Launch script to run microbenchmarks with different configuration.

#### launch_microbench_allconfig.py

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


## Steps to Run microbenchmark-experiments

The particular microbenchmarks we are using in this tutorial were originally developed at the University of Wisconsin-Madison. This microbenchmark suite is divided into different control, execution and memory benchmarks. We will use system emulation (SE) mode of gem5 to run these microbenchmarks with gem5.

To download the microbench source code:

```sh
git clone https://github.com/darchr/microbench.git
```
Commit the source of microbenchmarks to the micro-tests repo (so that the current version of microbenchmarks becomes a part of your working reposiotry).

```sh
git add microbench/
git commit -m "Add microbenchmarks"
```

compile the benchmarks:

```sh
cd microbench
make
```

To create python3 virtual environment:

```sh
virtualenv -p python3 venv
source venv/bin/activate
```

Run the database (if not already running) using (run this command after creating a directory):

```sh
docker run -p 27017:27017 -v <absolute path to the created directory>:/data/db --name mongo-<some tag> -d mongo
```

Run a celery server using (unless this experiment is run by someone in DArchR):

```sh
celery -E -A gem5art.tasks.celery worker --autoscale=[number of workers],0
```

(For users inside DArchR follow these [steps](#using-shared-celery-server) to run your experiments using centralized celery server.)


 There are two launch scripts to micro-benchmarks.

- [launch-scripts/launch_microbenchmarks.py](launch_microbenchmark.py)
: Launch script to run basic microbenchmark experiment for all cpu.

- [launch-scripts/launch_microbench_allconfig.py](launch_microbench_allconfig.py)
: Launch script to run microbenchmarks with different configuration.

#### launch_microbench_allconfig.py

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


## Steps to Run microbenchmark-experiments

The particular microbenchmarks we are using in this tutorial were originally developed at the University of Wisconsin-Madison. This microbenchmark suite is divided into different control, execution and memory benchmarks. We will use system emulation (SE) mode of gem5 to run these microbenchmarks with gem5.

To download the microbench source code:

```sh
git clone https://github.com/darchr/microbench.git
```
Commit the source of microbenchmarks to the micro-tests repo (so that the current version of microbenchmarks becomes a part of your working reposiotry).

```sh
git add microbench/
git commit -m "Add microbenchmarks"
```

compile the benchmarks:

```sh
cd microbench
make
```

To create python3 virtual environment:

```sh
virtualenv -p python3 venv
source venv/bin/activate
```

Run the database (if not already running) using (run this command after creating a directory):

```sh
docker run -p 27017:27017 -v <absolute path to the created directory>:/data/db --name mongo-<some tag> -d mongo
```

Run a celery server using (unless this experiment is run by someone in DArchR):

```sh
celery -E -A gem5art.tasks.celery worker --autoscale=[number of workers],0
```

(For users inside DArchR follow these [steps](#using-shared-celery-server) to run your experiments using centralized celery server.)


 There are two launch scripts to micro-benchmarks.

- [launch-scripts/launch_microbenchmarks.py](launch_microbenchmark.py)
: Launch script to run basic microbenchmark experiment for all cpu.

- [launch-scripts/launch_microbench_allconfig.py](launch_microbench_allconfig.py)
: Launch script to run microbenchmarks with different configuration.

#### launch_microbench_allconfig.py

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





## Using Shared Celery Server

To use shared celery server for all users on a machine, you need to follow the following steps:

Add a celery user:

```sh
useradd celery
```

Also, create a group named celery:

```sh
groupadd celery
```

Add celery user to the celery group:

```sh
usermod -a -G celery celery
```

All users which want to use celery server should be part of this group.

Next, create an init script named celery.service with the following contents (which will be used to start the celery server):

```
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=celery
Group=celery
EnvironmentFile=-/etc/conf.d/celery
WorkingDirectory=/opt/celery
ExecStart=/bin/sh -c '${CELERY_BIN} multi start $CELERYD_NODES \
	-A $CELERY_APP --pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} \
	--loglevel="${CELERYD_LOG_LEVEL}" $CELERYD_OPTS'
ExecStop=/bin/sh -c '${CELERY_BIN} multi stopwait $CELERYD_NODES \
	--pidfile=${CELERYD_PID_FILE}'
ExecReload=/bin/sh -c '${CELERY_BIN} multi restart $CELERYD_NODES \
	-A $CELERY_APP --pidfile=${CELERYD_PID_FILE} --logfile=${CELERYD_LOG_FILE} \
	--loglevel="${CELERYD_LOG_LEVEL}" $CELERYD_OPTS'
Restart=always

[Install]
WantedBy=multi-user.target
```
You can modify the `EnvironmentFile` or `WorkingDirectory` parameters above, depending on your set-up.
For details on how to create this script, [see](https://docs.celeryproject.org/en/latest/userguide/daemonizing.html).

The `EnvironmentFile` we are using is here:

```
# See
# http://docs.celeryproject.org/en/latest/userguide/daemonizing.html#usage-systemd

CELERY_APP="gem5art.tasks"
CELERYD_NODES="worker"
CELERYD_OPTS="--autoscale=48,0"
CELERY_BIN="/opt/celery/virtualenv/bin/celery"
CELERYD_PID_FILE="/opt/celery/%n.pid"
CELERYD_LOG_FILE="/opt/celery/%n%I.log"
CELERYD_LOG_LEVEL="INFO"
CELERYD_CHDIR="/opt/celery/"
CELERYD_USER="celery"
CELERYD_GROUP="celery"
CELERY_CREATE_DIRS=1
```

One of the important environment variable used above is `CELERYD_OPTS`, which determines how many worker threads will be used by the celery server.
You can modify this based on your own system.

We need to install the gem5art package to a python virtual environment in our working directory for celery (/opt/celery in our case):

```sh
virtualenv -p python3 venv
source venv/bin/activate
pip install gem5art-artifact gem5art-run gem5art-tasks
```

In order to allow any user part of the celery group to make changes to the virtual environment, we need to change group permissions:

```sh
chmod g+w -R venv
```

Now, to start the celery service:

```sh
systemctl start celery.service
```

Since, some of the gem5 jobs use kvm, we need to add `celery` user to the kvm group as well:

```sh
usermod -a -G kvm celery
```

In order for this change (and other similar changes) to make an effect, we need to restart the celery service:

```sh
systemctl restart celery.service
```

**Note**: Server should be restarted, whenever, gem5art is upgraded as well.


Now, when a user wants to use celery shared server to run their jobs, they need to do following:

Add yourself to celery group

```sh
usermod -a -G celery user-name
```

Change the group of your results directory by doing:

```sh
chgrp -R celery results/
```

You will also have to change the permissions of your results directory, to make it writeable by celery group:

```sh
chmod -R g+s results/
```

The above command sets the gid bit for results directory which makes sure that the group of the files created inside results/ will be that of the parent directory itself.

Make sure that the gem5 binary has execute permission for the group (g+x).
