#!/usr/bin/python
import socket
import sys

def get_my_ip_address():
	''' Returns the IP address of the client in dotted decimal notation '''
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.connect(("8.8.8.8", 80))
	except socket.error , msg:
		print 'Cannot connect to internet. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
	# s.connect(("8.8.8.8", 80))
	ip_address = s.getsockname()[0]
	s.close()
	return ip_address

def get_destination_ip_address(network_location):
	''' Returns the IP address of the given network location'''
	try:
		return socket.gethostbyname(network_location)
	except socket.error, msg:
		print msg
		sys.exit()
