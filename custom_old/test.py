from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink

def topology():
        net = Mininet(controller=RemoteController, link=TCLink, switch=OVSKernelSwitch)

        # Add hosts and switches
        h1 = net.addHost('h1', ip="10.0.1.10/24", mac="00:00:00:00:00:01")
        h2 = net.addHost('h2', ip="10.0.1.11/24", mac="00:00:00:00:00:02")
        r1 = net.addHost('r1')
        s1 = net.addSwitch('s1')
        s2 = net.addSwitch('s2')
        c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

        net.addLink(r1, s1)
        net.addLink(r1, s2)
        net.addLink(h1, s1)
        net.addLink(h2, s2)
        net.build()

        c0.start()
        s1.start([c0])
        s2.start([c0])
        h1.cmd("ip route add default via 10.0.1.1")

        print("*** Running CLI")
        CLI( net )

        print("*** Stopping network")
        net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology() 