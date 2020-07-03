#!/usr/bin/env python

from jsonrpclib import Server
import jsonrpclib
import syslog
import sys

thisSwitch = Server( "unix:/var/run/command-api.sock")

def main():
    syslog.openlog( 'bgp-check-py', 0, syslog.LOG_LOCAL4 )
    result = thisSwitch.runCmds(1, [ 'show ip bgp 192.168.33.1/32 detail vrf CUST-A' ], "json")
    if '192.168.33.1/32' in result[0]['vrfs']['CUST-A']['bgpRouteEntries'].keys() and \
       '1234:5678' in result[0]['vrfs']['CUST-A']['bgpRouteEntries']['192.168.33.1/32']['bgpRoutePaths'][0]['routeDetail']['communityList']:
        print("BGP-CHECK-LOG: BGP community 1234:5678 detected!")
        syslog.syslog( '%BGP-CHECK-LOG: BGP community 1234:5678 detected!')
        # apply change
        # check if RM is already applied so we dont have to repeat the step
        result = thisSwitch.runCmds( 1, ['show route-map RM-R5-OUT'], "json")
        if not ("10" in result[0]["routeMaps"]["RM-R5-OUT"]["entries"].keys() and \
                        result[0]["routeMaps"]["RM-R5-OUT"]["entries"]["10"]["matchRules"]["prefixList"] == "PL-ADV-R5" and \
                        result[0]["routeMaps"]["RM-R5-OUT"]["entries"]["10"]["filterType"] == "permit"):
            result = thisSwitch.runCmds( 1, ["enable", "configure", "ip prefix-list PL-ADV-R5 permit 192.168.33.1/32", "route-map RM-R5-OUT permit 10", "match ip address prefix-list PL-ADV-R5", "end"], "json")
            syslog.syslog( '%BGP-CHECK-LOG: BGP RM change applied towards R5')
    else:
        result = thisSwitch.runCmds( 1, ['show route-map RM-R5-OUT'], "json")
        if "10" in result[0]["routeMaps"]["RM-R5-OUT"]["entries"]:
            result = thisSwitch.runCmds( 1, ["enable", "configure", "no route-map RM-R5-OUT permit 10", "no ip prefix-list PL-ADV-R5 permit 192.168.33.1/32", "end"], "json")
            syslog.syslog( '%BGP-CHECK-LOG: BGP RM towards R5 removed')

if __name__ == "__main__":
   main()
