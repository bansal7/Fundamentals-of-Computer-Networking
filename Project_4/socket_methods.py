#!/usr/bin/python
import socket
import sys

def create_raw_send_socket():
    '''Returns a raw socket for sending packets'''
    try:
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except socket.error , msg:
        print 'Send socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    return send_socket

def create_raw_receive_socket():
    '''Returns a raw socket for receiving packets'''
    try:
        receive_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except socket.error , msg:
        print 'Receive socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    return receive_socket

