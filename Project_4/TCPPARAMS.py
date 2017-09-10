#!/usr/bin/python
import random

RTO = 10
SRC_PORT = random.randrange(49152,65535)
# Globals (Will be edited by multiple people
PACKET_ID = 1   # CANNOT BE 0, Kernel replaces it with a random number if
                # you start with 0
SEQ_NUM   = random.randrange(10,100)
ACK_NUM	  = 0

PADDING_BYTE = "\x00"

# Receiver Flags will be edited every time a packet is received
RECEIVER_FIN_FLAG = 0
RECEIVER_SYN_FLAG = 0
RECEIVER_RST_FLAG = 0
RECEIVER_PSH_FLAG = 0
RECEIVER_ACK_FLAG = 0
RECEIVER_URG_FLAG = 0

# Receiver Flag indicators
FIN_FLAG_CODE = 1
SYN_FLAG_CODE = 2
RST_FLAG_CODE = 4
PSH_FLAG_CODE = 8
ACK_FLAG_CODE = 16
URG_FLAG_CODE = 32

# REQUIRED Next SEQ Number for in-order delivery of packets to application
REQ_SEQ_NUM = 0

# Global field that stores the data
FILENAME = ''

# User agent to prevent bot alarms at destination websites
USER_AGENT = 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
ENCODING   = 'Accept-Encoding: identity'
ACCEPT     = "Accept: */*"
CONN       = "Connection: Keep-Alive"
# Maximum SYN retries
MAX_SYN_RETRIES = 10

# Check if it is the first packet with headers
FIRST_PACKET_FLAG = 1
INVALID_RESPONSE = 0

# Checksum fail flags
TCP_CHECKSUM_FAIL_FLAG = 0
IP_CHECKSUM_FAIL_FLAG  = 0

# Number of Checksum fails
TCP_CHECKSUM_FAILS = 0
IP_CHECKSUM_FAILS  = 0

# Extra information
TCP_CHECKSUM_COUNT = 0
IP_CHECKSUM_COUNT = 0
