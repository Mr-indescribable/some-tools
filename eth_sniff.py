#!/usr/bin/python3
#coding: utf-8

import socket
import struct


MTU = 65536

ETH_PROTO_IP = 0x0800
ETH_PROTO_ALL = 0x0003

ETH_PROTO_IP_NS = 0x0080
ETH_PROTO_ALL_NS = 0x0300


sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, ETH_PROTO_IP_NS)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, MTU)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b'enp4s0')
# sock.bind(('enp4s0', 0x0800))


while True:
    r = sock.recv(MTU)

    print(r)
    print('\n--------------------------------------------\n')
