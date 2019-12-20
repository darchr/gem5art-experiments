# gem5art-experiments

This repository contains different files (launch scripts, gem5 configuration files, disk image and linux configuration files) needed to run experiments with gem5art. 
This README describes how to run different experiments with gem5art step-by-step and points to the detailed documentation on these experiments as well.


**Note:** The user should make sure to create a local git repository containing all files for a particular experiment (from this repository), and add a remote to that repository as well.

The commands to do this:

```
git init
git remote add origin https://your-remote-add/[any]-experiments.git
```

## Steps to Run Full System Linux Boot Tests

Once, you have downloaded all the files from [boot-experiments](boot-experiments/) folder of this repo, follow the following steps to run full system linux boot tests:

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

Finally, run the [launch script](boot-experiments/launch_boot_tests.py) to start running these experiments:

```sh
python launch_boot_tests.py
```

Details of these experiments can be seen in a tutorial [here](https://gem5art.readthedocs.io/en/latest/boot-tutorial.html).


## Steps to Run NAS Parallel Benchmarks

Once, you have downloaded all the files from [npb-experiments](npb-experiments/) folder of this repo, follow the following steps to run these experiments:

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

Finally, run the [launch script](npb-experiments/launch_npb_tests.py) to start running these experiments:

```sh
python launch_npb_tests.py
```

Details of these experiments can be seen in a tutorial [here](https://gem5art.readthedocs.io/en/latest/npb-tutorial.html).


## Steps to Run SPEC CPU 2006 Benchmarks

Once, you have downloaded all the files from [spec2006-experiments](spec2006-experiments/) folder of this repo, follow the following steps to run SPEC 2006 benchmarks with gem5art:

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
wget https://releases.hashicorp.com/packer/1.4.5/packer_1.4.5_linux_amd64.zip
unzip packer_1.4.5_linux_amd64.zip
rm packer_1.4.5_linux_amd64.zip

./packer validate spec2006/spec2006.json
./packer build spec2006/spec2006.json
```

To compile the linux kernel:
```sh
git clone --branch v4.19.83 --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/
mv linux linux-4.19.83
cp linux-configs/config.4.19.83 linux-4.19.83/.config
cd linux-4.19.83
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

For users inside DArchR follow these [steps](#using-shared-celery-server) to run your experiments using centralized celery server.

Finally, run the [launch script](spec2006-experiments/launch_spec_experiment.py) to start running these experiments:

```sh
python launch_spec_experiment.py
```

Details of these experiments can be seen in a tutorial [here](https://gem5art.readthedocs.io/en/latest/spec2006-tutorial.html).




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
WorkingDirectory=/data1/celery
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
CELERY_BIN="/data1/celery/virtualenv/bin/celery"
CELERYD_PID_FILE="/data1/celery/%n.pid"
CELERYD_LOG_FILE="/data1/celery/%n%I.log"
CELERYD_LOG_LEVEL="INFO"
CELERYD_CHDIR="/data1/celery/"
CELERYD_USER="celery"
CELERYD_GROUP="celery"
CELERY_CREATE_DIRS=1
```

One of the important environment variable used above is `CELERYD_OPTS`, which determines how many worker threads will be used by the celery server.
You can modify this based on your own system.

We need to install the gem5art package to a python virtual environment in our working directory for celery (/data1/celery in our case):

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
adduser celery kvm
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
