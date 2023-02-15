#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import Intf
from mininet.log import setLogLevel, info
from mininet.node import RemoteController

def myNetwork():
    net = Mininet(topo=None, build=False)

    info( '*** Adding controller\n' )
    net.addController(name='c0', controller=RemoteController, ip='10.71.52.7', port=6633)
    
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', dpid='1') # leaf1
    s2 = net.addSwitch('s2', dpid='2') # leaf2
    s3 = net.addSwitch('s3', dpid='3') # leaf3
 
    info( '*** Add links\n')

    net.addLink(s1, s2, 1, 1)
    net.addLink(s1, s3, 2, 1)
    net.addLink(s2, s3, 2, 2)
    
    info( '*** Starting network\n')
    net.start()

    # s1.cmdPrint('ovs-vsctl set interface s1-eth1 lldp:enable=true')
    # s1.cmdPrint('ovs-vsctl set interface s1-eth2 lldp:enable=true')
    # s2.cmdPrint('ovs-vsctl set interface s2-eth1 lldp:enable=true')
    # s2.cmdPrint('ovs-vsctl set interface s2-eth2 lldp:enable=true')
    # s3.cmdPrint('ovs-vsctl set interface s3-eth1 lldp:enable=true')
    # s3.cmdPrint('ovs-vsctl set interface s3-eth2 lldp:enable=true')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
