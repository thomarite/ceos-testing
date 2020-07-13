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

More details: https://blog.thomarite.uk/index.php/2020/05/25/mpls-segment-routing-arista-lab/

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
(testdir2) /testdir2/mpls-sr/nornir master$ python buid-config.py -b isis -c
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

# cEOS - docker - Napalm/Nornir Issue

I am using cEOS that is a container controlled via docker.
Nornir uses Napalm to connect to the cEOS containers
As cEOS containers relay on my laptop OS and filesystem, there are some commands that fail. It is not a napalm/norninr issue, it is a just a permissions issue between the container and my FS.

I need this hack to be able to write in /mnt/flash although it still throws an error when writing to startup-config (but it writes...)

```
docker# chmod o+w zfs/graph/*/mnt/flash/.checkpoints
docker# chmod o+w zfs/graph/*/mnt/flash  --> I can write on /mnt/flash needed for napalm-commit
```

# TEXTFSM

Under the nornir forlder, I wanted to try TEXTFSM, so I had to download the templates. More info in https://github.com/networktocode/ntc-templates

```
$ cd nornir
$ git clone https://github.com/networktocode/ntc-templates.git ntc-templates
```

Then you need to set an ENV var for TEXTFSM, you can do it via cli/bashr or via the script (my choice in this particular case)

```
$ export NET_TEXTFSM=~/nornir/ntc_templates/templates
$ update your .bashrc with the above line

or 

python:
import os
os.environ['NET_TEXTFSM'] = './ntc-templates/templates'

```

This example it is a nornir task that uses netmiko to send "show ip interface brief" and we receive a structured reply thanks to textfsm.

```
(testdir2) /ceos-testing/nornir master$ python test-textfsm.py 
netmiko_send_command************************************************************
* r1 ** changed : False ********************************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
[ { 'interface': 'Ethernet1',
    'ip': '10.0.12.1/30',
    'mtu': '1500',
    'protocol': 'up',
    'status': 'up'},
  { 'interface': 'Ethernet2',
    'ip': '10.0.13.1/30',
    'mtu': '1500',
    'protocol': 'up',
    'status': 'up'},
  { 'interface': 'Loopback1',
    'ip': '10.0.0.1/32',
    'mtu': '65535',
    'protocol': 'up',
    'status': 'up'},
  { 'interface': 'Loopback2',
    'ip': '192.168.0.1/32',
    'mtu': '65535',
    'protocol': 'up',
    'status': 'up'}]
...
```
# NetBox

I struggled. All info here:

https://blog.thomarite.uk/index.php/2020/07/07/netbox/

```
/netbox-example$ tree -L 2
.
├── netbox-docker
│   ├── build-functions
│   ├── build-latest.sh
│   ├── build-next.sh
│   ├── build.sh
│   ├── configuration
│   ├── docker
│   ├── docker-compose.test.yml
│   ├── docker-compose.yml         <-- modify ports nginx 8080:8080
│   ├── Dockerfile
│   ├── env                        <-- netbox.env: define NAPALM_USERNAME and NAPALM_PASSWORD
│   ├── initializers
│   ├── LICENSE
│   ├── README.md
│   ├── reports
│   ├── scripts
│   ├── startup_scripts
│   ├── test.sh
│   └── VERSION
├── nornir-napalm-netbox-demo
│   ├── config.yaml              <-- modify url/port
│   ├── data
│   ├── Makefile
│   ├── nornir.log
│   ├── README.md
│   ├── requirements.txt        <-- you will have to remove the version of some packages
│   └── scripts                 <-- modify secrets and python scripts to use your python env
└── venv
    ├── bin
    ├── include
    ├── lib
    └── share
```


# Ansible

Hardwork to get this working with the latest ansible 2.9 and eos modules as most of the examples I was following were failing.

I am not going to discover the fire regarding ansible so not much explanation here

Having the virtualenv enabled, just install ansible with pip

```
(testdir2) /arista/testdir2$ python -m pip install ansible
```

Important files to take into account. 

ansible.cfg -- define where is your inventory (./ansible-hosts in my case)

ansible-hosts -- defintion of your hosts. You can define the user/pass and ports for ssh and https. Taking into account that each device uses a different port.

group_vars/ceoslab.yaml -- You need to define specific vars for using the eapi and the networks_os.

The file structure:

```
/ansible master$ tree 
.
├── ansible.cfg
├── ansible-hosts
├── group_vars
│   └── ceoslab.yaml
└── playbooks
    ├── collect-facts-cli.yaml
    └── collect-facts-eapi.yaml
```

So I have two basic playbooks to collect facts using SSH and EAPI (recommended to use -vvv for extra logging...)

```
/ansible master$ ansible-playbook playbooks/collect-facts-eapi.yaml -vvv
/ansible master$ ansible-playbook playbooks/collect-facts-cli.yaml -vvv
```

I will try to add more examples.


# Netconf / Openconfig

These has been quite hard. This simple test to get the interface config via netcong is based on [Anton Karneliuk blog](https://karneliuk.com/2018/08/openconfig-part-3-advanced-openconfig-w-ansible-for-arista-eos-cisco-ios-xr-and-nokia-sr-os-route-policy-bgp-and-interfaces-again): 


# To-Do

To-Dos
 - test batfish
 - test ZTP
 - add some alpine linux boxes to simulate customers, etc.

# Diagrams

All of them have bee done using https://draw.io

This is the ring topoloy (6 devices) - check the topology folder to use if via docker-topo

![](images/mpls-sr-ceos.png)


This is the 3-node topoloy (still a ring :) This is good for testing on your laptop as 6 devices can put a bit of a strain on resources.

![](images/3-node-mpls-sr-ceos.png)


Example from EVE-NG on GCP using vEOS

[![asciicast](https://asciinema.org/a/Dk1PAxDBamzQMechaOWbN5NV9.svg)](https://asciinema.org/a/l57G2ppeejuslQ2FJl4gu3xNx)
