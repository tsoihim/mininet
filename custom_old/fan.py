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
    #s4 = net.addSwitch('s4', dpid='4') # leaf4
    #s5 = net.addSwitch('s5', dpid='5') # leaf5
    #s6 = net.addSwitch('s6', dpid='6') # leaf6
    #s7 = net.addSwitch('s7', dpid='7') # leaf7
 
    info( '*** Add hosts\n')
    #h1 = net.addHost('h1', ip='10.0.10.11', mac='22:33:ff:2a:de:a1')
    #h2 = net.addHost('h2', ip='10.0.10.12', mac='22:33:ff:2a:de:a2')
    #h3 = net.addHost('h3', ip='10.0.10.13', mac='22:33:ff:2a:de:a3')
    #h4 = net.addHost('h4', ip='10.0.10.14', mac='22:33:ff:2a:de:a4')
    #h5 = net.addHost('h5', ip='10.0.10.15', mac='22:33:ff:2a:de:a5')
    #h6 = net.addHost('h6', ip='10.0.10.16', mac='22:33:ff:2a:de:a6')
    
    info( '*** Add links\n')

    net.addLink(s1, s2, 1, 1)
    net.addLink(s1, s3, 2, 1)
    net.addLink(s2, s3, 2, 2)
    
    #net.addLink(h1, s1, 1, 5)
    #net.addLink(h2, s1, 1, 6)
    #net.addLink(h3, s2, 1, 5)
    #net.addLink(h4, s2, 1, 6)
    #net.addLink(h5, s3, 1, 5)
    #net.addLink(h6, s3, 1, 6)

    info( '*** Starting network\n')
    net.start()

    s1.cmdPrint("ovs-vsctl del-controller s1")
    s1.cmdPrint("ovs-ofctl del-flows s1")
    s1.cmdPrint("ovs-ofctl add-flow s1 dl_type=0x88cc,actions=drop")
    s1.cmdPrint("ovs-ofctl add-flow s1 in_port=1,actions=output:2")
    s1.cmdPrint("ovs-ofctl add-flow s1 in_port=2,actions=output:1")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
