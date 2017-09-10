#!/usr/bin/python
import socket
import re
from struct import *
import TCPPARAMS

def get_checksum(msg):
    '''returns checksum of the given packet'''
    s = 0
    for i in range(0, len(msg), 2):
        w = (ord(msg[i])<<8) + ord(msg[i+1])
        s += w
        if s >= 0x10000:
            carry = s & 0x10000
            s -= 0x10000
            s += (carry >> 16)
    #   Complement and mask to 4 byte short
    s = ~s & 0xffff
    return s

def is_the_packet_from_dst(packet,dst):
    '''Returns true if the received packet is
    the packet from our connected remote site'''
    packet = packet[0]
    ip_header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    s_addr = socket.inet_ntoa(iph[8]);
    return (str(s_addr) == str(dst))

def prepare_packet(packet_info):
    '''Returns a packet to be sent by using the contents of the given dictionary'''
    #===================================================================================================================
    # IP Headers construction
    #===================================================================================================================
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0

    ip_tot_len = 20+20+len(packet_info['data'])
    ip_id = packet_info['packet_id']
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = socket.IPPROTO_TCP
    ip_check = 0    # kernel will fill the correct checksum
    ip_saddr = socket.inet_aton (packet_info['src'])
    ip_daddr = socket.inet_aton (packet_info['dst'])
    ip_ihl_ver = (ip_ver << 4) + ip_ihl

    if(ip_id> 65535): ip_id = 0
    ip_header_before_checksum = pack('!BBHHHBBH4s4s',ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check,\
                     ip_saddr, ip_daddr)

    if len(ip_header_before_checksum) % 2 != 0:
        ip_header_before_checksum+=TCPPARAMS.PADDING_BYTE
    ip_check = get_checksum(ip_header_before_checksum)
    # Pack the header again
    ip_header = pack('!BBHHHBBH4s4s',ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check,\
                     ip_saddr, ip_daddr)

    #===================================================================================================================
    # TCP Headers construction
    #===================================================================================================================
    tcp_source  = packet_info['src_port']
    tcp_dest    = 80    # Destination port for HTTP
    tcp_seq     = packet_info['seq_num']
    tcp_ack_seq = packet_info['ack_num']
    tcp_doff    = 5
    tcp_fin = packet_info['fin_flag']
    tcp_syn = packet_info['syn_flag']
    tcp_rst = packet_info['rst_flag']
    tcp_psh = packet_info['psh_flag']
    tcp_ack = packet_info['ack_flag']
    tcp_urg = 0
    tcp_window = socket.htons (5840)    #   Maximum allowed window size
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)

    # the ! in the pack format string means network order
    tcp_header = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  \
                      tcp_window, tcp_check, tcp_urg_ptr)

    user_data = packet_info['data']

    # pseudo header fields
    source_address = socket.inet_aton(packet_info['src'])
    dest_address = socket.inet_aton(packet_info['dst'])
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(user_data)

    pseudo_header = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length)
    pseudo_header = pseudo_header + tcp_header + user_data

    # New checksum code
    if len(pseudo_header) % 2 != 0:
        pseudo_header+=TCPPARAMS.PADDING_BYTE
    tcp_check = get_checksum(pseudo_header)

    tcp_header = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags, \
                      tcp_window,tcp_check,tcp_urg_ptr)

    packet = ip_header + tcp_header + user_data
    return packet

def display_packet(packet):
    '''Displays the various fields of IP and TCP Header of given packet'''
    packet = packet[0]
    ip_header = packet[0:20]

    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    ttl = iph[5]
    protocol = iph[6]
    s_addr = socket.inet_ntoa(iph[8]);
    d_addr = socket.inet_ntoa(iph[9]);

    print "IP Headers:"
    print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' \
            + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)

    tcp_header = packet[iph_length:iph_length+20]
    tcph = unpack('!HHLLBBHHH' , tcp_header)

    source_port = tcph[0]
    dest_port   = tcph[1]
    sequence    = tcph[2]
    acknowledgement = tcph[3]
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4
    print "TCP Headers:"
    print 'Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + \
          str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length)

def check_IP_header_checksum(packet):
    ''' Verify whether the IP checksum in the given packet is equal to the calculated IP checksum.
    Set a flag to indicate whether the checksum has failed'''
    packet = packet[0]
    ip_header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)

    received_IP_checksum = hex(iph[7])
    received_IP_Packet = pack('!BBHHHBBH4s4s' , iph[0], iph[1], iph[2], iph[3], iph[4], iph[5], iph[6], 0, iph[8], iph[9])
    calculated_IP_checksum = get_checksum(received_IP_Packet)

    if received_IP_checksum != hex(calculated_IP_checksum):
        TCPPARAMS.IP_CHECKSUM_FAILS += 1
        TCPPARAMS.IP_CHECKSUM_FAIL_FLAG = 1
    else:
        TCPPARAMS.IP_CHECKSUM_FAIL_FLAG = 0
    TCPPARAMS.IP_CHECKSUM_COUNT += 1

def check_TCP_header_checksum(packet):
    ''' Verify whether the TCP checksum in the given packet is equal to the calculated TCP checksum.
    Set a flag to indicate whether the checksum has failed'''

    packet = packet[0]
    ip_header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    version_ihl = iph[0]
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    tcp_header = packet[iph_length:iph_length+20]
    tcph = unpack('!HHLLBBHHH' , tcp_header)
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4
    h_size = iph_length + tcph_length * 4
    data_size = len(packet) - h_size

    received_data         = packet[h_size:]
    received_tcp_checksum = hex(tcph[7])
    tcp_options_length  = (tcph_length * 4) - 20
    end_of_options      = 40 + tcp_options_length

    reconstructed_tcp = pack('!HHLLBBHHH' , tcph[0], tcph[1], tcph[2], tcph[3], tcph[4], tcph[5], tcph[6], 0, tcph[8])

    tcp_segment_length = len(tcp_header)+ tcp_options_length + data_size
    pseudo_header = pack('!4s4sBBH' , iph[8], iph[9], 0, iph[6], tcp_segment_length)
    pseudo_header += reconstructed_tcp

    if tcp_options_length != 0:
        pseudo_header += packet[40:end_of_options]

    pseudo_header += received_data
    pseudo_header_length = len(pseudo_header)
    if(pseudo_header_length % 2 != 0):
        pseudo_header += TCPPARAMS.PADDING_BYTE
    tcp_calculated_checksum = hex(get_checksum(pseudo_header))

    if received_tcp_checksum != tcp_calculated_checksum:
        TCPPARAMS.TCP_CHECKSUM_FAILS += 1
        TCPPARAMS.TCP_CHECKSUM_FAIL_FLAG = 1
    else:
        TCPPARAMS.TCP_CHECKSUM_FAIL_FLAG = 0
    TCPPARAMS.TCP_CHECKSUM_COUNT += 1

def process_packet(packet):
    ''' Process the given packet to set the ACK Number, SEQ Number and PACKET_ID for the next
    packet. Also store the contents of the data(if it exists) in the file'''
    packet = packet[0]
    ip_header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    version_ihl = iph[0]
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    tcp_header = packet[iph_length:iph_length+20]
    tcph = unpack('!HHLLBBHHH' , tcp_header)
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4
    h_size = iph_length + tcph_length * 4
    flags = tcph[5]
    store_server_flags(flags)
    data_size = len(packet) - h_size

    # Update the TCP Parameters for next packet dispatch
    # tcph[2] contains sequence number of the dst
    # tcph[3] contains the acknowledgement number given by dst (Our sequence number + 1)
    TCPPARAMS.SEQ_NUM = tcph[3]
    TCPPARAMS.ACK_NUM  = tcph[2]
    TCPPARAMS.PACKET_ID += 1

    if(TCPPARAMS.REQ_SEQ_NUM == 0):
        if(data_size == 0):
            TCPPARAMS.ACK_NUM  += 1
        else:
            TCPPARAMS.ACK_NUM  += data_size
    else:
        if TCPPARAMS.ACK_NUM != TCPPARAMS.REQ_SEQ_NUM:
            # This means that, server has sent an out of order packet
            # Don't update your ACK_NUM and keep sending duplicate ACK packets
            TCPPARAMS.ACK_NUM  += 0
        else:
            # Expected data has arrived in order.
            # But we should also check if this packet does not have any data
            if(data_size == 0):
                # Even if there is no data, we still need to acknowledge
                # the received packet, hence increment by 1
                TCPPARAMS.ACK_NUM  += 1
            else:
                # Required order packet is received.
                # data_size is not 0, so extract the contents and store it
                TCPPARAMS.ACK_NUM  += data_size
                TCPPARAMS.REQ_SEQ_NUM = TCPPARAMS.ACK_NUM
                data = packet[h_size:]

                if TCPPARAMS.FIRST_PACKET_FLAG == 1:
                    if data.find("HTTP/1.1 200 OK") == -1:
                        print "ERROR: Given URL did not respond with an HTTP status code of 200"
                        TCPPARAMS.INVALID_RESPONSE = 1
                    TCPPARAMS.FIRST_PACKET_FLAG = 0

                if data.find("\r\n\r\n")!= -1 and data.find("image") != -1:
                    content = data.split("\r\n\r\n",1)[1]
                    if(data.find('Transfer-Encoding') != -1):
                        if(data.find("\r\n")!= -1):
                            content = content.split('\r\n',1)[1]

                elif data.find("\r\n\r\n")!= -1 and data.find("HTTP/1.1 200 OK") != -1:
                    data    = data.split("\r\n\r\n",1)[1]
                    if(data.find("\r\n")!= -1):
                        content = data.split('\r\n',1)[1]
                    else:
                        content = data
                elif data.find("0\r\n\r\n")!= -1:
                    content = data.rsplit("\r\n\r\n",1)[0].rsplit("\r\n",1)[0]
                elif data.find("HTTP/1.1 200 OK") != -1 and data.find("\r\n\r\n") == -1:
                    # This case could occur if a server decides to send such a short packet
                    # which has only the header which continues into next packet.
                    # So this packet will contain a truncated header and NO data (and hence no \r\n\r\n)
                    content = ""
                else:
                    # If you receive a packet which contains \r\n\r\n (which should be ideally found in HTTP 200OK
                    # packet) or in the ending, we need to split it and accept the latter part only
                    if len(data.split("\r\n\r\n",1)) != 1:
                        data = data.split("\r\n\r\n",1)[1]
                    # Also, remove those chunked encoding byte lengths embedded in text as:
                    content = re.sub(r'\r\n[0-9a-fA-F]+\r\n',"",data)

                f = open(TCPPARAMS.FILENAME,'a')
                f.write(content)
                f.close()

def get_seq_num(packet):
    ''' Returns the sequence number in the TCP header of the given packet'''
    packet = packet[0]
    ip_header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    version_ihl = iph[0]
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    tcp_header = packet[iph_length:iph_length+20]
    tcph = unpack('!HHLLBBHHH' , tcp_header)
    # tcph[2] contains sequence number of the dst
    return tcph[2]

def store_server_flags(flags):
    ''' Extract the given set of flags and store them in global file'''
    TCPPARAMS.RECEIVER_FIN_FLAG = flags & TCPPARAMS.FIN_FLAG_CODE
    TCPPARAMS.RECEIVER_SYN_FLAG = flags & TCPPARAMS.SYN_FLAG_CODE
    TCPPARAMS.RECEIVER_RST_FLAG = flags & TCPPARAMS.RST_FLAG_CODE
    TCPPARAMS.RECEIVER_PSH_FLAG = flags & TCPPARAMS.PSH_FLAG_CODE
    TCPPARAMS.RECEIVER_ACK_FLAG = flags & TCPPARAMS.ACK_FLAG_CODE
    TCPPARAMS.RECEIVER_URG_FLAG = flags & TCPPARAMS.URG_FLAG_CODE

def get_data_size(packet):
    ''' Returns the size of data payload in the given packet'''
    packet = packet[0]
    ip_header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    version_ihl = iph[0]
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    tcp_header = packet[iph_length:iph_length+20]
    tcph = unpack('!HHLLBBHHH' , tcp_header)
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4
    h_size = iph_length + tcph_length * 4
    data_size = len(packet) - h_size
    return data_size

def store(packet):
    ''' Store the incoming packet flags in the global file '''
    packet = packet[0]
    ip_header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    version_ihl = iph[0]
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    tcp_header = packet[iph_length:iph_length+20]
    tcph = unpack('!HHLLBBHHH' , tcp_header)
    flags = tcph[5]
    store_server_flags(flags)