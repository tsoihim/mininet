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
    net.addController(name='c0', controller=RemoteController, ip='127.0.0.1', port=6644)
    
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', dpid='1') # leaf1
    s2 = net.addSwitch('s2', dpid='2') # leaf2
    s3 = net.addSwitch('s3', dpid='3') # hub1
    s4 = net.addSwitch('s4', dpid='4') # hub1-1
    s5 = net.addSwitch('s5', dpid='5') # hub1-2
    s6 = net.addSwitch('s6', dpid='6') # hub2
    
    info( '*** Add links\n')
    net.addLink(s1, s2, 1, 1)

    net.addLink(s1, s3, 2, 1) 
    net.addLink(s3, s4, 2, 1) 
    net.addLink(s3, s5, 3, 1) 
    net.addLink(s4, s5, 2, 2) 
    
    net.addLink(s2, s6, 2, 1) 
    net.addLink(s2, s6, 3, 2) 
    
    info( '*** Starting network\n')
    net.start()

    s1.cmdPrint('ovs-vsctl set-controller s1 tcp:127.0.0.1:6633')
    s2.cmdPrint('ovs-vsctl set-controller s2 tcp:127.0.0.1:6633')

    s3.cmdPrint('ovs-vsctl del-controller s3')
    s3.cmdPrint('ovs-ofctl del-flows s3')
    s3.cmdPrint('ovs-ofctl add-flow s3 in_port=1,actions=output:2,3')
    s3.cmdPrint('ovs-ofctl add-flow s3 in_port=2,actions=output:1')
    s3.cmdPrint('ovs-ofctl add-flow s3 in_port=3,actions=output:1')

    s4.cmdPrint('ovs-vsctl del-controller s4')
    s4.cmdPrint('ovs-ofctl del-flows s4')
    s4.cmdPrint('ovs-ofctl add-flow s4 in_port=1,actions=output:2')
    s4.cmdPrint('ovs-ofctl add-flow s4 in_port=2,actions=output:1')

    s5.cmdPrint('ovs-vsctl del-controller s5')
    s5.cmdPrint('ovs-ofctl del-flows s5')
    s5.cmdPrint('ovs-ofctl add-flow s5 in_port=2,actions=output:1')
    s5.cmdPrint('ovs-ofctl add-flow s5 in_port=1,actions=output:2')

    s6.cmdPrint('ovs-vsctl del-controller s6')
    s6.cmdPrint('ovs-ofctl del-flows s6')
    s6.cmdPrint('ovs-ofctl add-flow s6 in_port=1,actions=output:2')
    s6.cmdPrint('ovs-ofctl add-flow s6 in_port=2,actions=output:1')
    # s4.cmdPrint('ovs-ofctl add-flow s4 in_port=2,actions=output:1')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
