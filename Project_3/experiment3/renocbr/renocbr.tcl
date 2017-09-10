# =======================================================
# File: renocbr.tcl
# Purpose: Trace TCP Reno and CBR fairness for a queue
# Arguments: <QUEUE-ALGORITHM> <CBR> <QUEUE-SIZE>
# Author(s): Amit Kulkarni and Bansal Shah
# Last changed: Tue Nov 17 18:53:19 EST 2015
# =======================================================
# Create a simulator
  set ns [new Simulator]

# Grab the argument value of queue provided by python
  set given_queue [lindex $argv 0]

# Grab the argument value of CBR provided by python
  set given_cbr [lindex $argv 1]mb

# Grab the argument value of queue size provided by python
  set given_queuesize [lindex $argv 2]

# =======================================================
# Define different colors for data flows
  $ns color 1 Blue
  $ns color 2 Red
 
# =======================================================
# Open Data trace file
  set tracefile [open renocbr.tr w]
  $ns trace-all $tracefile

# =======================================================
# Open the NAM trace file
#  set namfile [open out.nam w]
#  $ns namtrace-all $namfile

# =======================================================
# Define a 'finish' procedure
  proc finish {} {
     global ns 
#     global namfile
     global tracefile
     $ns flush-trace
     close $tracefile
#     close $namfile
#     We don't need to see the animator everytime
#     exec nam out.nam &
     exit 0
  }

# =======================================================
# Create this configuration:
#
#             1                4
#    10Mb/10ms \  10Mb/10ms   / 10Mb/10ms
#               2 -----------3
#    10Mb/10ms /              \ 10Mb/10ms
#             5                6
#
#  TCP1:  1 -> 4
#  CBR:   5 -> 6

# =======================================================
# Create the nodes:
  set n1 [$ns node]
  set n2 [$ns node]
  set n3 [$ns node]
  set n4 [$ns node]
  set n5 [$ns node]
  set n6 [$ns node]
# =======================================================

# Create the links:
#  $ns duplex-link $n1 $n2 10Mb 10ms DropTail
#  $ns duplex-link $n5 $n2 10Mb 10ms DropTail
#  $ns duplex-link $n2 $n3 10Mb 10ms DropTail
#  $ns duplex-link $n3 $n4 10Mb 10ms DropTail
#  $ns duplex-link $n3 $n6 10Mb 10ms DropTail

  $ns duplex-link $n1 $n2 10Mb 10ms $given_queue
  $ns duplex-link $n5 $n2 10Mb 10ms $given_queue
  $ns duplex-link $n2 $n3 10Mb 10ms $given_queue
  $ns duplex-link $n3 $n4 10Mb 10ms $given_queue
  $ns duplex-link $n3 $n6 10Mb 10ms $given_queue
# =======================================================
# Monitor the queue for link (n1-n2). (for NAM)
  $ns duplex-link-op $n2 $n3 queuePos 0.5

# =======================================================
# Give node position (for NAM)
  $ns duplex-link-op  $n1 $n2 orient right-down
  $ns duplex-link-op  $n5 $n2 orient right-up
  $ns duplex-link-op  $n2 $n3 orient right
  $ns duplex-link-op  $n3 $n4 orient right-up
  $ns duplex-link-op  $n3 $n6 orient right-down

# =======================================================
# Set Queue Size of link (n2-n3) to 5
  $ns queue-limit $n2 $n3 $given_queuesize

# =======================================================
# Setup a TCP connection
  set tcp0 [new Agent/TCP/Reno]
  $ns attach-agent $n1 $tcp0

  set sink0 [new Agent/TCPSink]
  $ns attach-agent $n4 $sink0

# =======================================================
# Connect the TCP Source and the Sink
  $ns connect $tcp0 $sink0
  $tcp0 set fid_ 1
  $tcp0 set class_ 1
  $tcp0 set packetSize_ 1000

# =======================================================
# Setup a FTP over TCP connection
  set ftp0 [new Application/FTP]
  $ftp0 attach-agent $tcp0
  $ftp0 set type_ FTP

# =======================================================
# Create a UDP agent and attach it to node n5
  set udp0 [new Agent/UDP]
  $ns attach-agent $n5 $udp0

# =======================================================
# Create a CBR traffic source and attach it to udp0
  set cbr0 [new Application/Traffic/CBR]
  $cbr0 set type_ CBR
  $cbr0 set packetSize_ 1000
  $cbr0 set rate_ $given_cbr
  $cbr0 attach-agent $udp0

# =======================================================
# Connect UDP Source to Null
  set null0 [new Agent/Null]
  $ns attach-agent $n6 $null0
  $ns connect $udp0 $null0
  $udp0 set fid_ 2


# =======================================================
# Specify the time durations of flows

  $ns at 0.5 "$ftp0 start"
  $ns at 3.5 "$cbr0 start"
  $ns at 13.5 "$cbr0 stop"
  $ns at 14.5 "$ftp0 stop"

# =======================================================
# Set simulation end time
  $ns at 15.0 "finish"

# Print CBR packet size and interval
 puts "Running renocbr.tcl with..."
 puts "CBR rate = [$cbr0 set rate_]"
 puts "Queue Algorithm = $given_queue"
 puts "Queue size = $given_queuesize"

# =======================================================
# Run the simulation
  $ns run

