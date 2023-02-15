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
    net.addController(name='c0', controller=RemoteController, ip='10.0.73.20', port=6633)
    
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', dpid='1') # spine
    s2 = net.addSwitch('s2', dpid='2') # leaf
    
    info( '*** Add hosts\n')
    h1 = net.addHost('h1', ip='10.0.10.11', mac='00:00:17:2a:de:a1') # oracle
    h2 = net.addHost('h2', ip='10.0.10.12', mac='fc:ff:aa:2a:de:a2') # IEEE
    h3 = net.addHost('h3', ip='10.0.10.11', mac='00:00:17:2a:de:a1') # apple
    h4 = net.addHost('h4', ip='10.0.10.12', mac='fc:ff:aa:2a:de:a2') # huawei
    
    info( '*** Add links\n')

    net.addLink(s1, s2, 1, 1)
    
    net.addLink(h1, s2, 1, 5)
    net.addLink(h2, s2, 1, 6)
    net.addLink(h3, s2, 1, 7)
    net.addLink(h4, s2, 1, 8)

    h2.cmdPrint('ip link add link h2-eth1 h2-eth1.10 type vlan proto 802.1Q id 10')
    h2.cmdPrint('ip link set h2-eth1 up')
    h2.cmdPrint('ip addr add 10.0.10.12/24 dev h2-eth1.10')

    # h3.cmdPrint('ip link add link h3-eth1 h3-eth1.20 type vlan proto 802.1Q id 20')
    # h3.cmdPrint('ip link set h3-eth1 up')
    # h3.cmdPrint('ip addr add 10.0.10.13/24 dev h3-eth1.20')

    # h4.cmdPrint('ip link add link h4-eth1 h4-eth1.20 type vlan proto 802.1Q id 20')
    # h4.cmdPrint('ip link set h4-eth1 up')
    # h4.cmdPrint('ip addr add 10.0.10.14/24 dev h4-eth1.20')

    info( '*** Starting network\n')
    net.start()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
