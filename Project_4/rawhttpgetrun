#!/usr/bin/python
import argparse
from urlparse import urlparse
import subprocess
import time
import sys
import os

# User modules
import socket_methods
import packet_processor
import utilities
import TCPPARAMS

#Fetch the page URL from command line
parser = argparse.ArgumentParser()
parser.add_argument("url", type=str, help="Please provide a URL to fetch")
args = parser.parse_args()
URL  = args.url
URL  = urlparse(URL)
# URL = urlparse('http://www.ccs.neu.edu/home/cbw/4700/2MB.log')
network_location = URL.hostname

# Prepare a file to store the contents
path = URL.path
if path == '': path = '/'

if path == '/':
	# Just fetch the index.html
	subprocess.check_output("rm -f index.html",shell=True)
	subprocess.check_output("touch index.html",shell=True)
	TCPPARAMS.FILENAME= 'index.html'
else:
	filename = path.split('/')[-1]
	if filename == '':
		subprocess.check_output("rm -f index.html",shell=True)
		subprocess.check_output("touch index.html",shell=True)
		TCPPARAMS.FILENAME = 'index.html'
	else:
		subprocess.check_output("rm -f "+filename,shell=True)
		subprocess.check_output("touch "+filename,shell=True)
		TCPPARAMS.FILENAME = filename


def cleanup_and_close():
	''' Close the open sockets and exit the program'''
	receive_socket.close()
	send_socket.close()
	sys.exit()

def get_start_time():
	''' Returns the current time'''
	return time.time()

def get_one_minute_timeout(start_time):
	''' Returns a time after 1 minute of given time'''
	return start_time+60

def get_program_termination_time(start_time):
	''' Returns a time after 3 minutes of given time'''
	return start_time+180


def connection_teardown():
	''' Send an ACK response for the FIN-ACK sent by server
	Also, sends a FIN-ACK to the server to indicate end of data from client'''
	while(True):
		packet['packet_id'] = TCPPARAMS.PACKET_ID
		packet['ack_flag'] = 1
		packet['fin_flag'] = 0
		packet['seq_num']   = TCPPARAMS.SEQ_NUM
		packet['ack_num']   = TCPPARAMS.ACK_NUM
		ack_packet = packet_processor.prepare_packet(packet)
		send_socket.sendto(ack_packet , (DST_IP_ADDRESS, 0 ))

		# Server is done sending its data, tell him that even you are done with deal
		TCPPARAMS.PACKET_ID += 1
		packet['packet_id'] = TCPPARAMS.PACKET_ID
		packet['seq_num']   = TCPPARAMS.SEQ_NUM
		packet['ack_num']   = TCPPARAMS.ACK_NUM

		packet['ack_flag'] = 1
		packet['fin_flag'] = 1
		packet['psh_flag'] = 0
		packet['data'] = ''
		# Send the FIN packet
		fin_packet = packet_processor.prepare_packet(packet)
		send_socket.sendto(fin_packet , (DST_IP_ADDRESS, 0 ))
		break

# Common data structure containing sufficient information to build a packet
# This data structure will be used for passing information
packet = {'src': 0,
		  'dst': 0,
		  'packet_id': 0,
		  'src_port': TCPPARAMS.SRC_PORT,
		  'seq_num': 0,
		  'ack_num': 0,
		  'syn_flag': 0,
		  'ack_flag': 0,
		  'fin_flag': 0,
		  'psh_flag': 0,
		  'rst_flag': 0,
		  'data': ''}

received_packet = {'src': 0, 'seq_num': 0,'ack_num': 0,'fin_flag': 0}

# Constant for inserting carriage return and newline character in GET request
CRLF = "\r\n"

SRC_IP_ADDRESS = utilities.get_my_ip_address()
DST_IP_ADDRESS = utilities.get_destination_ip_address(network_location)


program_start_time = time.time()

packet['src'] = SRC_IP_ADDRESS
packet['dst'] = DST_IP_ADDRESS
packet['packet_id'] = TCPPARAMS.PACKET_ID
packet['src_port'] = TCPPARAMS.SRC_PORT
packet['seq_num'] = TCPPARAMS.SEQ_NUM
packet['ack_flag'] =TCPPARAMS.ACK_NUM
packet['syn_flag'] = 1
packet['ack_flag'] = 0
packet['fin_flag'] = 0
packet['psh_flag'] = 0
packet['rst_flag'] = 0
packet['data'] = ''

# Create send and receive sockets
send_socket = socket_methods.create_raw_send_socket()
receive_socket = socket_methods.create_raw_receive_socket()


def check_retries_exceeded(retries, msg):
	''' If we are out of retries, print an error message and exit'''
	if retries < 1:
		print "ERROR: Maximum "+ msg +" retries exceeded, program terminated"
		sys.exit()

def send_syn_request():
	''' Sends a SYN Request and exits the while loop after receiving a SYN-ACK'''

	handshake_syn_packet = packet_processor.prepare_packet(packet)
	# Timeout setting:
	syn_start_time = get_start_time()
	syn_timeout    = get_one_minute_timeout(syn_start_time)
	syn_program_termination_timeout = get_program_termination_time(syn_start_time)
	send_socket.sendto(handshake_syn_packet, (DST_IP_ADDRESS, 0))
	while(True):
		# Note the current time and check if it has exceeded the timeout
		current_time = time.time()
		TCPPARAMS.MAX_SYN_RETRIES -= 1
		if current_time > syn_program_termination_timeout:
			print "ERROR: No response for SYN request, program terminated"
			cleanup_and_close()
		check_retries_exceeded(TCPPARAMS.MAX_SYN_RETRIES,"SYN request")
		if current_time > syn_timeout: send_syn_request()

		# RECEIVE A SYN-ACK PACKET
		received_packet = receive_socket.recvfrom(4096)
		if packet_processor.is_the_packet_from_dst(received_packet,DST_IP_ADDRESS):
			packet_processor.process_packet(received_packet)
			if TCPPARAMS.RECEIVER_ACK_FLAG and TCPPARAMS.RECEIVER_SYN_FLAG:
				# It means, our receive socket has received a packet from intended destination
				# if ACK and SYN Flags are set, it means we have received a SYN-ACK packet
				break

# SYN request
send_syn_request()

# SEND AN ACK PACKET
# Change the parameters which were updated
packet['packet_id'] = TCPPARAMS.PACKET_ID
packet['seq_num']   = TCPPARAMS.SEQ_NUM
packet['ack_num']   = TCPPARAMS.ACK_NUM
packet['syn_flag'] = 0
packet['ack_flag'] = 1
handshake_ack_packet = packet_processor.prepare_packet(packet)
send_socket.sendto(handshake_ack_packet, (DST_IP_ADDRESS, 0))

#=======================================================================================================================
# REQUEST SOME DATA
#=======================================================================================================================
TCPPARAMS.PACKET_ID += 1
packet['psh_flag'] = 1
packet['ack_flag'] = 1
packet['packet_id'] = TCPPARAMS.PACKET_ID
packet['data'] = "GET "+path+" HTTP/1.1"+CRLF+\
				 "Host: "+network_location+CRLF+\
				 TCPPARAMS.USER_AGENT+CRLF+\
				 TCPPARAMS.ACCEPT+CRLF+\
				 TCPPARAMS.ENCODING+CRLF+\
				 TCPPARAMS.CONN+CRLF+CRLF

data_len = len(packet['data'])
psh_packet = packet_processor.prepare_packet(packet)

# Store the starting sequence number of the server which it has promised
TCPPARAMS.REQ_SEQ_NUM = TCPPARAMS.ACK_NUM

data_request_start_time = get_start_time()
data_request_max_time   = get_program_termination_time(data_request_start_time)

send_socket.sendto(psh_packet , (DST_IP_ADDRESS, 0 ))

def retransmit_duplicate_ack():
	''' Retransmits a Duplicate ACK since we had a timeout or we did not receive a packet in order'''
	global data_request_start_time
	global data_request_max_time
	global packet
	global send_socket
	packet['psh_flag'] = 0
	packet['ack_flag'] = 1
	TCPPARAMS.PACKET_ID += 1
	packet['packet_id'] = TCPPARAMS.PACKET_ID
	packet['seq_num']   = TCPPARAMS.SEQ_NUM
	packet['ack_num']   = TCPPARAMS.ACK_NUM
	packet['data'] = ''
	dup_ack_data_packet = packet_processor.prepare_packet(packet)

	# Reset the timers for this new packet
	data_request_start_time = get_start_time()
	data_request_max_time   = get_program_termination_time(data_request_start_time)

	send_socket.sendto(dup_ack_data_packet , (DST_IP_ADDRESS, 0 ))

while(True):

	current_time = time.time()
	if current_time > data_request_max_time:
		print "ERROR: Connection timed out, program terminated"
		cleanup_and_close()
	received_packet = receive_socket.recvfrom(4096)
	if packet_processor.is_the_packet_from_dst(received_packet,DST_IP_ADDRESS):

		packet_processor.store(received_packet)

		if(packet_processor.get_data_size(received_packet) == 0 and TCPPARAMS.RECEIVER_FIN_FLAG == 0):
			# If it is an ACK Packet and not a FIN packet with no data, dont send any ACK
			continue
		if(packet_processor.get_seq_num(received_packet) != TCPPARAMS.REQ_SEQ_NUM):
			# We still haven't got the required Data, so basically we have to request the server with
			# duplicate ACK

			retransmit_duplicate_ack()
			continue

		packet_processor.process_packet(received_packet)

		if TCPPARAMS.RECEIVER_FIN_FLAG and TCPPARAMS.RECEIVER_ACK_FLAG:
			connection_teardown()
			break

		if(TCPPARAMS.RECEIVER_ACK_FLAG or (TCPPARAMS.RECEIVER_ACK_FLAG and TCPPARAMS.RECEIVER_PSH_FLAG)):

			# Before sending an ACK, check if the checksums are correct.
			# If not, retransmit a DUP-ACK requesting the same packet again
			packet_processor.check_IP_header_checksum(received_packet)
			packet_processor.check_TCP_header_checksum(received_packet)

			if TCPPARAMS.IP_CHECKSUM_FAIL_FLAG or TCPPARAMS.TCP_CHECKSUM_FAIL_FLAG:
				retransmit_duplicate_ack()

			packet['psh_flag'] = 0
			packet['ack_flag'] = 1
			packet['packet_id'] = TCPPARAMS.PACKET_ID
			packet['seq_num']   = TCPPARAMS.SEQ_NUM
			packet['ack_num']   = TCPPARAMS.ACK_NUM
			packet['data'] = ''
			ack_data_packet = packet_processor.prepare_packet(packet)
			send_socket.sendto(ack_data_packet, (DST_IP_ADDRESS, 0))

if TCPPARAMS.INVALID_RESPONSE == 1:
	os.remove(TCPPARAMS.FILENAME)


cleanup_and_close()