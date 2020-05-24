# mpls-sr in Arista cEOS

I am using docker-topo from https://github.com/networkop/docker-topo to build the lab and the script ceosctl from https://github.com/etedor/ceos-lab-box to run some commands in all devices.

So for getting docker-topo to work follow the instructions from the original repo.

You will need to create an account in arista.com (it is free) to downloand the cEOS images.

My laptop is running Debian 10 Testing, Intel i7 and 8GB RAM. It struggles a bit with the 6 containers running.

The goal is to build a basic MPLS Segment Routing lab using ISIS as IGP and EVPN for providing a L2/3 VPN.

Issues found:
 - Need to disable all PIM processes ==> constant cores  -> can't run config, save config etc
 - mtu only 1500 -> isis doesnt come up --- I was expecting to be able to run jumbo frames... I am so naive...
 - show isis neighbor command fails but the routing shows the prefixes so it works under the hood.

This is the network diagram

![](images/mpls-sr-ceos.png)
