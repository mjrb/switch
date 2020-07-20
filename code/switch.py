from gevent import monkey
monkey.patch_all()

import json
from socket import socket, AF_PACKET, SOCK_RAW, htons
import sys
from time import sleep
from datetime import datetime

import gevent
from scapy.all import Ether, IPv6, IP, ARP

# ether type
ETH_P_ALL = 0x0003
ETH_P_IP4 = 0x0800
ETH_P_ARP = 0x0806
ETH_P_IP6 = 0x86DD

# parse config
with open(sys.argv[1]) as f:
    config = json.load(f)

ifaces = {}
mac_table = {}
my_macs = set(config['macs'])

def listener(iface):
    s = socket(AF_PACKET, SOCK_RAW, proto=htons(ETH_P_ALL))
    s.bind((iface, 0))
    ifaces[iface] = s
    print(f'listening to {iface}')
    while True:
        data = s.recv(4096)
        decoded = Ether(data)
        print(f'{iface}: {decoded.src} -> {decoded.dst} [{hex(decoded.type)}]')
        if decoded.type == ETH_P_IP6:
            i = IPv6(decoded.payload)
            print(f'    IPV6 {i.src} -> {i.dst} [{hex(i.nh)}]')
        elif decoded.type == ETH_P_IP4:
            i = IP(decoded.payload)
            print(f'    IPV4 {i.src} -> {i.dst} [{hex(i.proto)}]')
        elif decoded.type == ETH_P_ARP:
            a = ARP(decoded.payload)
            print(f'    ARP {a.psrc}({a.hwsrc}) -> {a.pdst}({a.hwdst})')

        # ignore packets ment for us
        if decoded.dst in my_macs or decoded.src in my_macs:
            continue

        # remember this mac for this interface, or update it. unless its the multicast address
        #if (not decoded.src in mac_table or mac_table.get(decoded.src) != iface) and decoded.src != 'FF:FF:FF:FF:FF:FF':
        #    mac_table[decoded.src] = {'iface': iface, 'since': datetime.now()}

        # remove from mactable if entry is too old
        #if decoded.dst in mac_table and (mac_table[decoded.dst]['since'] - datetime.now()).total_seconds() > config.ttl:
        #    del mac_table[decoded.dst]

        # figure out where to send
        if decoded.dst in mac_table:
            dsts = [mac_table[decoded.dst]['iface']]
        else:
            dsts = ifaces.keys()

        # send to destinations
        for dst in dsts:
            if dst != iface:
                bs = ifaces[dst].send(data)
                print(f'    sent {dst} {bs} bytes')

for iface in config['ifaces']:
    gevent.spawn(listener, iface)
while True:
    sleep(1)
