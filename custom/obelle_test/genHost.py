#!/usr/bin/env python

import sys
import socket 
import struct
import json, requests 
import argparse

ctrlIp = "127.0.0.1"
baseIp = 167772161 # 10.0.0.0
asyncPort = 9999

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

def insertData(data, tableName):
    url = "http://%s:%s/a-sync/dictionaries/%s" % (ctrlIp, asyncPort, tableName)
    response = requests.post(url, data=data)
    try:
        if response.status_code != 200 :
            raise Exception('')
    except Exception as e:
        print("ERROR: Failed to create A-Sync table record\n")
        sys.exit(1)

def getData(tableName):
	url = "http://%s:%s/a-sync/%sTable" % (ctrlIp, asyncPort, tableName)
	response = requests.get(url)
	try:
		data = response.json()
		return data
	except Exception as e:
		print("ERROR: Failed to get A-Sync table record\n")
		sys.exit(1)

### Make a-sync table data for test
def genHostData(hostNum):
    for i in range(hostNum):
        hostIp = baseIp + i
        data = '{\
            "vlanId": "0",\
            "portNo": "1",\
            "dpid": "%d",\
            "groupId" : "0",\
            "dlAddr" : "fc:d8:48:2a:de:a2",\
            "nwAddr": "%s",\
            "manufacturer": "Apple, Inc.",\
            "timestamp": "2022/09/14 06:20:16.899302679",\
            "status": "OB_HOST_VALID"\
        }' % (hostNum, int2Ip(hostIp))
        insertData(data, 'host')
    print(" - generate %d hostData\n" % hostNum)

# Entry point
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # ToDo - add validity and max value check
    parser.add_argument("--ctrl", dest="ctrlIp", action="store", default='127.0.0.1')
    parser.add_argument("--host", type=int, dest="hostNum", action="store", default=10)
    args = parser.parse_args()

    ctrlIp = args.ctrlIp

    print('*** Creating A-Sync table records')
    genHostData(args.hostNum)
    print('*** %d hosts registered\n' % len(getData('Host')))
