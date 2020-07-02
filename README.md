# Intro

Use docker-topo to build some network topologies using Arista cEOS (mainly MPLS SR) and test other tools like ansible, napalm, nornir, batfish, netbox, etc. Other topologies in my list are leaf-spine, Route-Reflectors, etc

# Installation

I am using docker-topo from https://github.com/networkop/docker-topo to build the lab and the script ceosctl from https://github.com/etedor/ceos-lab-box to run some commands in all devices.

So for getting docker-topo to work, follow the instructions from the original repo.

First time:

```
pyenv local 3.7.3
python3 -m pip install virtualenv
python3 -m virtualenv ceos-testing; cd ceos-testing
source bin/activate  /// to exit: $ deactivate
pip install git+https://github.com/networkop/docker-topo.git
-- clone this repo ---
git clone https://github.com/thomarite/mpls-sr-ceos.git mpls-sr
cd mpls-sr/topology
docker-topo --create ring.yml --> start-up topology
docker ps -a
docker-topo -s ring.yml   --> save config
docker-topo --create ring.yml --> destroy topology
deactivate
```

Afterwards:

```
cd ceos-testing
source bin/activate
cd mpls-sr/topology
docker-topo --create ring.yml
docker ps -a
```

# Arista cEOS

You will need to create an account in arista.com (it is free) to downloand the cEOS images.

# Hardware

My laptop is running Debian 10 Testing, Intel i7 and 8GB RAM. It struggles a bit with the 6 containers running.


# MPLS Segment Routing

Most of the topologies are MPLS Segment Routing using ISIS as IGP and EVPN for providing a L2/3 VPN.

# Issues

 - Need to disable all PIM processes ==> constant cores  -> can't run config, save config etc
 - mtu only 1500 -> isis doesnt come up --- I was expecting to be able to run jumbo frames... I am so naive...
 - show isis neighbor command fails but the routing shows the prefixes so it works under the hood.
 - can't ping inside the L3VPN. I think it is something related to the broadcast of ARPs :( ==> Actually, MPLS Data Plane doesnt work in cEOS. You need to try vEOS and be sure you have a ethernet interface in the VRF!!! (Lo or SVI are not enough to bring up properly the VRF at kernetl level - https://eos.arista.com/forum/see-bgp-routes-unable-to-ping/

```
r01#bash
bash-4.2# 
bash-4.2# ip netns exec ns-CUST-A tcpdump -i lo2
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on lo2, link-type EN10MB (Ethernet), capture size 262144 bytes

^C12:43:03.027590 02:00:00:00:00:00 (oui Unknown) > Broadcast, ethertype ARP (0x0806), length 42: Request who-has 192.168.0.6 tell 192.168.0.1, length 28
12:43:04.028753 02:00:00:00:00:00 (oui Unknown) > Broadcast, ethertype ARP (0x0806), length 42: Request who-has 192.168.0.6 tell 192.168.0.1, length 28
12:43:05.052753 02:00:00:00:00:00 (oui Unknown) > Broadcast, ethertype ARP (0x0806), length 42: Request who-has 192.168.0.6 tell 192.168.0.1, length 28

3 packets captured
3 packets received by filter
0 packets dropped by kernel
bash-4.2# 

```

# Nornir

In the "nornir" folder you can find a python script "buid-config.py" using nornir to build BGP and ISIS config (via jinja2) and use napalm to push the config. All the inventory is based on the 3-node topology but it is easy to change it to a different one. You need to install the python libraries from requirements.txt

This is the scructure. 

```
├── buid-config.py
├── config.yaml <-------------- nornir config file
├── inventory <---------------- nornir inventoriy files and devices
│   ├── defaults.yaml
│   ├── groups.yaml
│   ├── hosts.yaml
│   └── host_vars
│       ├── r1.yaml
│       ├── r2.yaml
│       └── r3.yaml
├── nornir.log
├── render  <------------------- rendered configs
│   ├── r1
│   │   ├── bgp.txt
│   │   └── isis.txt
│   ├── r2
│   │   ├── bgp.txt
│   │   └── isis.txt
│   └── r3
│       ├── bgp.txt
│       └── isis.txt
├── requirements.txt
└── templates <----------------- jinja2 templates
    ├── eos-bgp.j2
    └── eos-isis.j2
```

This is an example:

```
(testdir2) go:1.7.5|py:3.7.3|/arista/testdir2/mpls-sr/nornir master$ python buid-config.py -b isis -c
------------
hostname: r1
task: deploy_config for isis
failed: False
logs: None
changed: False
diff:


------------
hostname: r2
task: deploy_config for isis
failed: False
logs: None
changed: False
diff:


------------
hostname: r3
task: deploy_config for isis
failed: False
logs: None
changed: False
diff:
```


# To-Do

To-Dos
 - test ansible
 - test batfish
 - test textfsm
 - test netbox
 - test ZTP
 - add some alpine linux boxes to simulate customers, etc.

This is the network diagram (using https://draw.io)

![](images/mpls-sr-ceos.png)


Example from EVE-NG on GCP using vEOS

[![asciicast](https://asciinema.org/a/Dk1PAxDBamzQMechaOWbN5NV9.svg)](https://asciinema.org/a/l57G2ppeejuslQ2FJl4gu3xNx)
