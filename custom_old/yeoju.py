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
    s1 = net.addSwitch('s1', dpid='1') # spine
    s2 = net.addSwitch('s2', dpid='2') # leaf
    
    info( '*** Add hosts\n')
    h1 = net.addHost('h1', ip='10.0.10.11', mac='22:33:ff:2a:de:a1')
    h2 = net.addHost('h2', ip='10.0.10.12', mac='22:33:ff:2a:de:a2')
    h3 = net.addHost('h3', ip='10.0.10.13', mac='22:33:ff:2a:de:a3')
    h4 = net.addHost('h4', ip='10.0.10.14', mac='22:33:ff:2a:de:a4')
    
    info( '*** Add links\n')

    net.addLink(s1, s2, 1, 1)
    
    net.addLink(h1, s2, 1, 5)
    net.addLink(h2, s2, 1, 6)
    net.addLink(h3, s2, 1, 7)
    net.addLink(h4, s2, 1, 8)

    info( '*** Starting network\n')
    net.start()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
