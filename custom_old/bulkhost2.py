#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import Intf
from mininet.log import setLogLevel, info
from mininet.node import RemoteController

import sys
import socket 
import struct
import json, urllib2
import argparse
import threading 

ctrlIp = '127.0.0.1'
dpNum = 5
hostPerDp = 5
baseIp = 167772161 # 10.0.0.0
dpList = [] 
hostList = [] 

def ip2Int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2Ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

### Make a-sync table data for test
def makeDpData():
    for i in range(dpNum):
        data = '{ \
            "groupId": 1, \
            "dpid": "%s" \
        }' % (i+1)
        insertData(data, 'spine_group_dp_connectivity')
        data = '{ \
            "groupId": 1, \
            "dpid": "%s", \
            "portNo": 1, \
            "portType": "UPLINK_PORT_TYPE_PHYSICAL", \
            "timestamp": "" \
        }' % (i+1)
        insertData(data, 'uplink_port')
    info(" - create uplink_port\n")
    info(" - create spine_group_dp_connectivity\n")

def makeSubnetData():
    data = '{ \
        "gatewayIp": "10.0.0.1", \
        "subnetCidr": "10.0.0.0/20", \
        "vlanId": 10, \
        "vrrpId": 0, \
        "groupId": 1, \
        "hostFiltering": false, \
        "subnetName": "STRESS_TEST", \
        "subnetDesc": "", \
        "vrfName": "", \
        "ipPimSparseMode": false \
    }'
    insertData(data, 'lan_subnet')
    info(" - create lan_subnet\n")

def insertData(data, tableName):
    url = "http://%s:%s/a-sync/dictionaries/%s" % (ctrlIp, '9999', tableName)
    request = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    try:
        response = urllib2.urlopen(request)
        if response.getcode() != 200 :
            raise Exception('')
    except Exception as e:
        info("ERROR: Failed to create A-Sync table record\n")
        sys.exit(1)

### make dps and hosts
def myNetwork():
    net = Mininet(topo=None, build=False)

    nodeJobs = []
    linkJobs = []
    packetJobs = []

    dpId = 1
    
    info('*** Adding controller\n' )
    net.addController(name='c0', controller=RemoteController, ip=ctrlIp, port=6633)
    
    info('*** Adding switches and hosts\n')
    # Add base switch
    s1 = net.addSwitch('s1', dpid='%d' % dpId)
    info('add base switch s%d\n' % (dpId))
    dpId += 1
    for i in range(dpNum): 
        thread = threading.Thread(target = addDp, args = (net, i, dpId))
        nodeJobs.append(thread)
        dpId += 1
    for j in nodeJobs:
        j.start()
    for j in nodeJobs:
        j.join()

    info('*** Adding links\n')
    for i in range(dpNum):
        net.addLink(s1, dpList[i], i+1, 1)
        thread = threading.Thread(target = addLink, args = (net, i))
        linkJobs.append(thread) 
    for j in linkJobs:
        j.start()
    for j in linkJobs:
        j.join()

    info('*** Starting network\n')
    net.start()

    s1.cmd('ovs-vsctl set-controller s1 tcp:127.0.0.1:6634')
    s1.cmd('ovs-ofctl del-flows s1')

    info('*** Pinging hosts\n')
    for i in range(dpNum):
        info('> hosts on s%s\n' % (i+1))
        thread = threading.Thread(target = pingTest, args = (net, hostList[i]))
        packetJobs.append(thread)
    for j in packetJobs:
        j.start()
    for j in packetJobs:
        j.join()

    CLI(net)
    net.stop()

# Node worker
def addDp(net, idx, dpId):
    dpHostList = []
    dpList[idx] = net.addSwitch('s%d' % dpId, dpid='%d' % dpId)
    info('add leaf switch s%d\n' % (dpId))
    for j in range(hostPerDp) :
        hostId = hostPerDp * idx + j + 1
        dpHostList.append(net.addHost('h%d' % hostId, ip=int2Ip(baseIp+hostId)))
        info(' - add host h%d\n' % hostId)
        hostId += 1
    hostList[idx] = dpHostList
    dpId += 1

# Link worker
def addLink(net, idx):
    for j in range(hostPerDp):
        net.addLink(dpList[idx], hostList[idx][j], j+2, 1)

# Packet worker
def pingTest(net, hosts):
    net.ping(hosts=hosts, timeout=1)

# Entry point
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # ToDo - add validity and max value check
    parser.add_argument("--ctrl", dest="ctrlIp", action="store", default='127.0.0.1')
    parser.add_argument("--dp", type=int, dest="dpNum", action="store", default=5)
    parser.add_argument("--host", type=int, dest="hostPerDp", action="store", default=5)
    args = parser.parse_args()

    ctrlIp = args.ctrlIp 
    dpNum = args.dpNum 
    hostPerDp = args.hostPerDp 
    dpList = [None] * dpNum 
    hostList = [None] * dpNum  

    setLogLevel('info')
    info('*** Creating A-Sync table records\n')
    makeDpData()
    makeSubnetData()
    myNetwork()