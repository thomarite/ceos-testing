from ncclient import manager
from ncclient.xml_ import to_ele

def execrpc(hostip, uname, passw, rpc):
   conn=manager.connect(host=hostip,port=22,username=uname,password=passw, timeout=60,hostkey_verify=False,
      device_params={'name':'default'})
   rpcreply = conn.dispatch(to_ele(rpc))
   print(rpcreply)
   conn.close_session()

def intfrpcvxlan_cli(vxlan_id, vlan, vni):
   intfrpc = """<nc:edit-config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
   <target>
   <running/>
   </target>
   <commands>
   <command>interface Vxlan%s</command>
   <command>vxlan vlan %s vni %s</command>
   </commands>
   </nc:edit-config>""" % (vxlan_id, vlan, vni)
   return (intfrpc)

def irbrpc(vrf, vlan, svi, bgpas, rd, imprt, exprt, vni):
   snetrpc = """<nc:edit-config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
   <target>
   <running/>
   </target>
   <commands>
   <command>interface vlan %s</command>
   <command>vrf %s</command>
   <command>ip address virtual %s/24</command>
   <command>ip attached-host route export</command>
   </commands>
   <config>
   <arista xmlns="http://arista.com/yang/experimental/eos">
   <eos>
   <evpn xmlns="http://arista.com/yang/experimental/eos/evpn">
   <evpn-instances>
   <evpn-instance>
   <name>%s</name>
   <config>
   <instance-type>VLAN</instance-type>
   <name>%s</name>
   <redistribute>LEARNED</redistribute>
   <redistribute>ROUTER_MAC</redistribute>
   <redistribute>HOST_ROUTE</redistribute>
   <route-distinguisher>%s</route-distinguisher>
   </config>
   <route-target>
   <config>
   <auto-export>false</auto-export>
   <export>%s</export>
   <import>%s</import>
   </config>
   </route-target>
   <vlans>
   <vlan>
   <vlan-id>%s</vlan-id>
   <config>
   <vlan-id>%s</vlan-id>
   </config>
   </vlan>
   </vlans>
   </evpn-instance>
   </evpn-instances>
   </evpn>
   </eos>
   </arista>
   <network-instances xmlns="http://openconfig.net/yang/network-instance"><network-instance>
   <name>default</name>
   <vlans>
   <vlan>
   <vlan-id>%s</vlan-id>
   <config>
   <mac-learning xmlns="http://arista.com/yang/openconfig/network-instance/vlan/augments">true</mac-learning>
   <name>VLAN_%s</name>
   <status>ACTIVE</status>
   <vlan-id>%s</vlan-id>
   </config>
   <members/>
   </vlan>
   </vlans>
   </network-instance>
   </network-instances>
   <interfaces xmlns="http://openconfig.net/yang/interfaces">
   <interface>
   <name>Vlan%s</name>
   <arista-varp xmlns="http://arista.com/yang/experimental/eos/varp/intf">
   <virtual-address>
   <config>
   <ip>%s</ip>
   <prefix-length>24</prefix-length>
   </config>
   </virtual-address>
   </arista-varp>
   <config>
   <description>VLAN_%s</description>
   <enabled>true</enabled>
   <name>Vlan%s</name>
   <tpid xmlns="http://openconfig.net/yang/vlan" xmlns:oc-vlan-types="http://openconfig.net/yang/vlan-types">oc-vlan-types:TPID_0X8100</tpid>
   <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:l3ipvlan</type>
   </config>
   <routed-vlan xmlns="http://openconfig.net/yang/vlan">
   <config>
   <vlan>Vlan%s</vlan>
   </config>
   </routed-vlan>
   </interface>
   </interfaces>
   </config>
   </nc:edit-config>""" % (vlan, vrf, svi, vlan, vlan, rd, exprt, imprt, vlan,
   vlan, vlan, vlan, vlan, vlan, svi, vlan, vlan, vlan)
   return (snetrpc)

vlan = '100'
vrf = 'CUST-A'
svi = '1.1.1.1'
bgpas = '1'
rd = '1:1'
exprt = '2:2'
imprt = '3:3'
vxlan_id = '1'
vni = '10000'
hostip = '172.27.0.4'
uname = 'tomas'
passw = 'tomas123'

def main():
    rpc = irbrpc(vrf, vlan, svi, bgpas, rd, imprt, exprt, vni)
    execrpc(hostip, uname, passw, rpc)
    rpc = intfrpcvxlan_cli(vxlan_id, vlan, vni)
    execrpc(hostip, uname, passw, rpc)

if __name__ == "__main__":
   main()
