# MPLS Segment Routing in Arista cEOS

I am using docker-topo from https://github.com/networkop/docker-topo to build the lab and the script ceosctl from https://github.com/etedor/ceos-lab-box to run some commands in all devices.

So for getting docker-topo to work follow the instructions from the original repo.

First time:

```
pyenv local 3.7.3
python3 -m pip install virtualenv
python3 -m virtualenv testdir; cd testdir
source bin/activate  /// to exit: $ deactivate
pip install git+https://github.com/networkop/docker-topo.git
-- clone this repo ---
docker-topo --create ring.yml --> start-up topology
docker ps -a
docker-topo -s ring.yml   --> save config
docker-topo --create ring.yml --> destroy topology
deactivate
```

Afterwards:

```
cd testdir
source bin/activate
docker-topo --create ring.yml
docker ps -a
```

You will need to create an account in arista.com (it is free) to downloand the cEOS images.

My laptop is running Debian 10 Testing, Intel i7 and 8GB RAM. It struggles a bit with the 6 containers running.

The goal is to build a basic MPLS Segment Routing lab using ISIS as IGP and EVPN for providing a L2/3 VPN.

Issues found:
 - Need to disable all PIM processes ==> constant cores  -> can't run config, save config etc
 - mtu only 1500 -> isis doesnt come up --- I was expecting to be able to run jumbo frames... I am so naive...
 - show isis neighbor command fails but the routing shows the prefixes so it works under the hood.

To-Dos
 - test ansible/napalm
 - test nornir
 - test batfish
 - add some alpine linux boxes to simulate customers, etc.

This is the network diagram (using https://draw.io)

![](images/mpls-sr-ceos.png)
