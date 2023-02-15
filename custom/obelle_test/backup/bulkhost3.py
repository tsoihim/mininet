#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import Intf
from mininet.log import setLogLevel, info
from mininet.node import RemoteController

import sys
import socket 
import struct
import json, requests 
import argparse
import time
import concurrent.futures

ctrlIp = '127.0.0.1'
dpNum = 5
hostPerDp = 5
iperfEnable = False
iperfDuration = 10 
iperfTotalBw = 20000000000 # unit : bps 
baseIp = 167772161 # 10.0.0.0
baseRuleNum = 13
hostRuleNum = 5
asyncPort = 9999
maxPool = 200 
dpList = []
hostList = [] 

def ip2Int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2Ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def numToSi(val):
    count = 0
    num = 0
    unit = '' 
    val_tmp = val

    while True:
        val_tmp /= 1000
        if val_tmp >= 1:
            num = int(val_tmp)
            count += 1
        else:
            break

    if count == 1:
        unit = 'K'
    elif count == 2:
        unit = 'M'
    elif count == 3:
        unit = 'G'
    # ToDo - exception

    return '%s%s' % (num, unit) 

### Make a-sync table data for test
def makeDpData():
    for i in range(dpNum):
        data = '{ \
            "groupId": 1, \
            "dpid": "%s" \
        }' % (i+2)
        insertData(data, 'spine_group_dp_connectivity')
        data = '{ \
            "groupId": 1, \
            "dpid": "%s", \
            "portNo": 1, \
            "portType": "UPLINK_PORT_TYPE_PHYSICAL", \
            "timestamp": "" \
        }' % (i+2)
        insertData(data, 'uplink_port')
    info(" - create uplink_port\n")
    info(" - create spine_group_dp_connectivity\n")

def makeSubnetData():
    data = '{ \
        "gatewayIp": "10.0.0.1", \
        "subnetCidr": "10.0.0.0/16", \
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
    url = "http://%s:%s/a-sync/dictionaries/%s" % (ctrlIp, asyncPort, tableName)
    response = requests.post(url, data=data)
    try:
        if response.status_code != 200 :
            raise Exception('')
    except Exception as e:
        info("ERROR: Failed to create A-Sync table record\n")
        sys.exit(1)

def getData(tableName):
	url = "http://%s:%s/a-sync/%sTable" % (ctrlIp, asyncPort, tableName)
	response = requests.get(url)
	try:
		reponse = requests.get(url)
		data = response.json()
		return data
	except Exception as e:
		info("ERROR: Failed to get A-Sync table record\n")
		sys.exit(1)

# Node worker
def addNode(net, idx):
    dpHostList = []
    dpId = idx+2
    dpList[idx] = net.addSwitch('s%d' % dpId, dpid='%x' % dpId, batch=True, protocols="OpenFlow13")
    for j in range(hostPerDp) :
        hostId = hostPerDp * idx + j + 1
        dpHostList.append(net.addHost('h%d' % hostId, ip=int2Ip(baseIp+hostId)))
        hostId += 1
    hostList[idx] = dpHostList

# Link worker
def addLink(net, idx):
    for j in range(hostPerDp):
        net.addLink(dpList[idx], hostList[idx][j], j+2, 1)

# Ping worker
def pingHost(net, hosts):
    for i, host in enumerate(hosts):
	    if i+1 == len(hosts):
		    break
	    net.ping([hosts[i], hosts[i+1]])

# Iperf worker
def iperfHost(net, hosts, duration, bandwidth):
    assert len(hosts) > 1
    net.iperf(hosts=[hosts[0], hosts[-1]], l4Type='UDP', seconds=duration, udpBw=bandwidth)

def writeStat(netBuildTime, totalRuleNum):
    statData = {}
    timeNow = time.strftime('%Y%m%d-%H%M%S', time.localtime()) 
    statData['date'] = timeNow
    statData['controller'] = ctrlIp
    statData['dpNum'] = dpNum
    statData['hostPerDp'] = hostPerDp
    statData['netBuildTime'] = "%.3f sec" % netBuildTime 
    statData['maxPool'] = maxPool
    statData['ruleNumPerDp'] = totalRuleNum 
    with open('./test_stat-%s.json' % timeNow, 'w') as f:
        json.dump(statData, f, indent=2)

### make dps and hosts
def myNetwork():
    net = Mininet(topo=None, build=False)

    # ToDo - worker result check
    nodeExecutor = concurrent.futures.ThreadPoolExecutor(maxPool)
    linkExecutor = concurrent.futures.ThreadPoolExecutor(maxPool)
    
    start = time.time()

    info('*** Adding controller\n' )
    net.addController(name='c0', controller=RemoteController, ip=ctrlIp, port=6633)
    
    info('*** Adding switches and hosts\n')
    # Add base switch
    s1 = net.addSwitch('s1', dpid='1')
    info('add base switch s1\n')
    for i in range(dpNum):
        info('add leaf switch s%d\n' % (i+2))
        info(' - add host h%d ~ h%d\n' % ((hostPerDp * i + 1), hostPerDp * (i + 1)))
        nodeExecutor.submit(addNode, net, i)
    nodeExecutor.shutdown(wait=True)

    info('*** Adding links\n')
    for i in range(dpNum):
        net.addLink(s1, dpList[i], i+1, 1)
        linkExecutor.submit(addLink, net, i) 
    linkExecutor.shutdown(wait=True)

    info('*** Starting network\n')
    net.start()

    netBuildTime = time.time() - start
    info("*** Starting network took %.3f seconds\n" % (netBuildTime))

    s1.cmd('ovs-vsctl delete-controller s1')
    s1.cmd('ovs-ofctl del-flows s1')

    while True:
        pingExecutor = concurrent.futures.ThreadPoolExecutor(maxPool)
        info('*** Ping hosts\n')
        for i in range(dpNum): 
            info('> hosts on s%s\n' % (i+2))
            pingExecutor.submit(pingHost, net, hostList[i])
        pingExecutor.shutdown(wait=True)

        registeredHostNum = len(getData('Host'))
        if registeredHostNum == dpNum * hostPerDp: 
            info('*** %s hosts registered by OBelle-Access\n' % registeredHostNum)
            break

    totalRuleNum = baseRuleNum + hostRuleNum * hostPerDp
    # info('*** Checking if %d rules installed on dps\n' % totalRuleNum)	
    # while True:
    #     info('Counting flow entries...\n')
    #     notInstalledDpNum = 0 
    #     isAllInstalled = True 
    #     for dp in dpList:
    #         rules = dp.cmd('ovs-ofctl dump-flows %s -O openflow13' % dp.name)
    #         ruleNum = rules.count('\n')
    #         if int(ruleNum) < totalRuleNum: 
    #             info(" - %s has only %s rules\n" % (dp.name, ruleNum))
    #             isAllInstalled = False 
    #             notInstalledDpNum+=1
    #     if isAllInstalled:
    #         info("*** %s rules successfully installed on %s datapaths\n" % (totalRuleNum, dpNum))
    #         break
    #     else :
    #         info(" -> %d dps still lack rules\n" % notInstalledDpNum)
    #     time.sleep(5)

    # write stat on ./test_stat.json
    info('*** Dumping test stats to json file\n')	
    writeStat(netBuildTime, totalRuleNum)

    # iperf
    if iperfEnable:
        iperfExecutor = concurrent.futures.ThreadPoolExecutor(maxPool)
        info('*** Iperf hosts\n')	
        for i in range(dpNum):
            info(' - h%d <---> h%d on s%s : \n' % ((hostPerDp * i + 1), hostPerDp * (i + 1), (i+2)))
            iperfExecutor.submit(iperfHost, net, [hostList[i][0], hostList[i][-1]], iperfDuration, numToSi(int(iperfTotalBw/dpNum)))
        iperfExecutor.shutdown(wait=True)
    
    CLI(net)
    net.stop()

# Entry point
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # ToDo - add validity and max value check
    parser.add_argument("--ctrl", dest="ctrlIp", action="store", default='127.0.0.1')
    parser.add_argument("--dp", type=int, dest="dpNum", action="store", default=5)
    parser.add_argument("--host", type=int, dest="hostPerDp", action="store", default=5)
    parser.add_argument("--iperf", type=bool, dest="iperfEnable", action="store", default=False)
    args = parser.parse_args()

    ctrlIp = args.ctrlIp 
    dpNum = args.dpNum 
    hostPerDp = args.hostPerDp 
    iperfEnable = args.iperfEnable
    dpList = [None] * dpNum 
    hostList = [None] * dpNum  

    setLogLevel('info')
    info('*** Creating A-Sync table records\n')
    makeDpData()
    makeSubnetData()
    myNetwork()
