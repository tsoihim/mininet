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
    net.addController(name='c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    # Add base switch
    r1 = net.addHost('r1')
    info('add base router r1\n')

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', dpid='1')
    net.addLink(r1, s1, 1, 1)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', ip='0.0.0.0', mac='22:33:ff:2a:de:a1')
    h2 = net.addHost('h2', ip='0.0.0.0', mac='22:33:ff:2a:de:a2')
    h3 = net.addHost('h3', ip='0.0.0.0', mac='22:33:ff:2a:de:a3')
    
    info( '*** Add links\n')
    net.addLink(h1, s1, 1, 2)
    net.addLink(h2, s1, 1, 3)
    net.addLink(h3, s1, 1, 4)

    info( '*** Starting network\n')
    net.start()
    
    h1.cmdPrint('dhclient')
    h2.cmdPrint('dhclient')
    h3.cmdPrint('dhclient')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
