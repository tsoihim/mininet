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
    net.addController(name='c0', controller=RemoteController, ip='10.71.52.8', port=6633)
    
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', dpid='1')
    s2 = net.addSwitch('s2', dpid='5')    
    info( '*** Add hosts\n')
    h1 = net.addHost('h1', ip='10.0.1.11', mac='22:33:ff:2a:de:a1')
    h2 = net.addHost('h2', ip='10.0.1.12', mac='22:33:ff:2a:de:a2')
    
    info( '*** Add links\n')
    net.addLink(h1, s1, 1, 11)
    net.addLink(h2, s1, 1, 12)
    net.addLink(s1, s2, 1, 1)

    info( '*** Starting network\n')
    net.start()

    #s1.cmdPrint('ovs-vsctl add-port s1')
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
