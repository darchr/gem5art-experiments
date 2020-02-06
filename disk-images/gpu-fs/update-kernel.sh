#!/bin/bash
echo 'Updating Kernel'

export DEBIAN_FRONTEND=noninteractive

apt update
apt install -y build-essential git 
apt install -y libncurses5-dev flex bison libssl-dev libelf-dev bc

cd /home/gem5

git clone https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

cd linux
git checkout v4.15.18

cp /boot/config-4.15.0-45-generic .config
yes '' | make oldconfig

make -j 16
make modules_install
make install

echo 'Kernel Update Done'

reboot
