#!/usr/bin/python
import socket
import sys
from constants import *

def create_socket():
	stream_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	return stream_socket

def connect_socket_to_host(stream_socket):
	try:
		stream_socket.connect((REMOTE_HOST, REMOTE_PORT))
	except socket.error as e:
		print("Cannot connect to ")
		print(REMOTE_HOST+" on port: "+str(REMOTE_PORT))
		print(e)
		print ('something\'s wrong with %s:%d. Exception type is %s' % (REMOTE_HOST, REMOTE_PORT, `e`))
		sys.exit()

	return stream_socket

