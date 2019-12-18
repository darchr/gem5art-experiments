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


