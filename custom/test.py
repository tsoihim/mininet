from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink

def topology():
        net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch )

        # Add hosts and switches
        h1 = net.addHost( 'h1', ip="10.0.1.10/24", mac="00:00:00:00:00:01" )
        h2 = net.addHost( 'h2', ip="10.0.1.20/24", mac="00:00:00:00:00:02" )

        r1 = net.addHost( 'r1')
        
        s1 = net.addSwitch( 's1')
        s2 = net.addSwitch( 's2')

        c0 = net.addController( 'c0', controller=RemoteController, ip='127.0.0.1', port=6633 )

        net.addLink( r1, s1 )
        net.addLink( r1, s2 )
        net.addLink( h1, s1 )
        net.addLink( h2, s2 )

        net.build()
        c0.start()
        s1.start( [c0] )
        s2.start( [c0] )

        r1.cmd("ip addr flush dev r1-eth0")
        r1.cmd("ip addr flush dev r1-eth1")
        r1.cmd("ip link set dev r1-eth0 address 00:00:5e:00:01:ff") 
        r1.cmd("ip link set dev r1-eth1 address 00:00:5e:00:01:ff") 
        r1.cmd("ip link add bond0 type bond")
        r1.cmd("ip link set r1-eth0 master bond0") 
        r1.cmd("ip link set r1-eth1 master bond0") 
        r1.cmd('ip link add link bond0 bond0.10 type vlan proto 802.1Q id 10')
        r1.cmd("ip link add link bond0 name bond.10 type vlan id 10")
        r1.cmd("ip link set bond0 up") 
        r1.cmd("ip addr add 10.0.1.1/24 brd + dev bond0.10")
        r1.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
        r1.cmdPrint("ip addr")
        r1.cmdPrint("ip route")
        
        h1.cmd("ip route add default via 10.0.1.1")
        h2.cmd("ip route add default via 10.0.1.1")

        s1.cmd("ovs-ofctl add-flow s1 priority=50,in_port=2,arp,actions=set_vlan_vid:10,output:1")
        s2.cmd("ovs-ofctl add-flow s2 priority=50,in_port=1,arp,actions=strip_vlan,output:2")
        s1.cmd("ovs-ofctl add-flow s1 priority=65,dl_dst=00:00:5e:00:01:ff,actions=set_vlan_vid:10,output:1")
        s1.cmd("ovs-ofctl add-flow s1 priority=65,dl_vlan=10,dl_dst=00:00:00:00:00:01,actions=strip_vlan,output:2")
        s2.cmd("ovs-ofctl add-flow s2 priority=50,in_port=2,arp,actions=set_vlan_vid:10,output:1")
        s2.cmd("ovs-ofctl add-flow s2 priority=50,in_port=1,arp,actions=strip_vlan,output:2")
        s2.cmd("ovs-ofctl add-flow s2 priority=65,dl_dst=00:00:5e:00:01:ff,actions=set_vlan_vid:10,output:1")
        s2.cmd("ovs-ofctl add-flow s2 priority=65,dl_vlan=10,dl_dst=00:00:00:00:00:02,actions=strip_vlan,output:2")

        print("*** Running CLI")
        CLI( net )

        print("*** Stopping network")
        net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology() 