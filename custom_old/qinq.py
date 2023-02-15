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
    
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', dpid='1')
    
    info( '*** Add hosts\n')
    h1 = net.addHost('h1', ip='10.0.10.11', mac='22:33:ff:2a:de:a1')
    h2 = net.addHost('h2', ip='10.0.10.12', mac='22:33:ff:2a:de:a1')
    h3 = net.addHost('h3', ip='10.0.10.13', mac='22:33:ff:2a:de:a1')
    h4 = net.addHost('h4', ip='10.0.10.12', mac='22:33:ff:2a:de:a1')
    # h3 = net.addHost('h3', ip='10.0.1.13', mac='22:33:ff:2a:de:a3')
    
    info( '*** Add links\n')
    net.addLink(h1, s1, 1, 1)
    net.addLink(h2, s1, 1, 2)
    net.addLink(h3, s1, 1, 3)
    net.addLink(h4, s1, 1, 4)

    info( '*** Starting network\n')
    net.start()

    h1.cmdPrint('ip link add link h1-eth1 h1-eth1.24 type vlan proto 802.1Q id 24')
    h1.cmdPrint('ip link add link h1-eth1.24 h1-eth1.24.36 type vlan proto 802.1Q id 36')
    h1.cmdPrint('ip link set h1-eth1 up')
    h1.cmdPrint('ip link set h1-eth1.24 up')
    h1.cmdPrint('ip addr add 10.0.1.11/24 dev h1-eth1.24.36')
    h1.cmdPrint('ip link')
    h1.cmdPrint('ip addr')

    h2.cmdPrint('ip link add link h2-eth1 h2-eth1.25 type vlan proto 802.1Q id 25')
    h2.cmdPrint('ip link add link h2-eth1.25 h2-eth1.25.36 type vlan proto 802.1Q id 36')
    h2.cmdPrint('ip link set h2-eth1 up')
    h2.cmdPrint('ip link set h2-eth1.25 up')
    h2.cmdPrint('ip addr add 10.0.1.12/24 dev h2-eth1.25.36')
    # h1.cmdPrint('vconfig add h1-eth1 111')
    # h1.cmdPrint('ifconfig h1-eth1.111')
    # h1.cmdPrint('vconfig add h1-eth1.111 211')
    # h1.cmdPrint('ifconfig h1-eth1.111.211 10.0.1.11 netmask 255.255.255.0')
    
    # h2.cmdPrint('vconfig set_name_type VLAN_PLUS_VID_NO_PAD')
    # h2.cmdPrint('vconfig add h2-eth1 111')
    # h2.cmdPrint('ifconfig vlan111 20.0.1.1 netmask 255.255.255.0 up')
    # h2.cmdPrint('vconfig add vlan111 212')
    # h2.cmdPrint('ifconfig vlan212 10.0.1.12 netmask 255.255.255.0 up')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
