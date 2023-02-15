import sys, os, socket, string, struct
import paramiko
import concurrent.futures

baseIp = 167790950

def ip2Int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2Ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def workon(host, idx):
    cmd = "cd /home/sdndev/mininet/custom/obelle_test; python3 bulkhost3.py --ctrl 10.0.73.20" 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='root', password='atto1234')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write('pwd\n')
    stdin.flush()
    print(host)
    print(stdout.readlines())

def main():
    hostNum = 1
    
    executor = concurrent.futures.ThreadPoolExecutor(hostNum)
    for i in range(hostNum):
        executor.submit(workon, int2Ip(baseIp+i), i)
    executor.shutdown(wait=True)

main()