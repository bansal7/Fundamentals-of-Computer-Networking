#!/usr/bin/python
import subprocess
import sys

if len(sys.argv) > 1:
        # Queueing Algorithm
	QUEUE_METHOD = sys.argv[1]
else:
        print "Please provide a queueing method [DropTail/RED]"
        sys.exit()

# Queue size
QUEUE_SIZE   = str(5)
# CBR RATE IN MBPS
CBR_RATE     = str(7.5)

# Increment factor
INCREMENT_FACTOR        =       0.5

START_TIME   = 0.0
END_TIME     = 0.5
MAX_TIME     = 15.0

# Find out the path of NS
NS           =       subprocess.check_output("whereis ns | awk '{print $2}'", shell=True).strip()

TCP_TO_NODE  = 3
CBR_TO_NODE  = 5

def throughputFinder():
	global START_TIME,END_TIME, MAX_TIME
	t = open("TCP_throughput.txt",'a')
	c = open("CBR_throughput.txt",'a')
	while(END_TIME<MAX_TIME):
		tcp_throughput = subprocess.check_output("awk -f tp.awk starttime="+str(START_TIME)+" endtime="+str(END_TIME)+" toNode="+str(TCP_TO_NODE)+" renocbr.tr",shell=True).strip()		
		cbr_throughput = subprocess.check_output("awk -f tp.awk starttime="+str(START_TIME)+" endtime="+str(END_TIME)+" toNode="+str(CBR_TO_NODE)+" renocbr.tr",shell=True).strip()		
#		print "Range: ("+str(START_TIME)+"-"+str(END_TIME)+") = "+tcp_throughput+" "+cbr_throughput
	        t.write(str(END_TIME)+ " " + str(tcp_throughput)+"\n")
	        c.write(str(END_TIME)+ " " + str(cbr_throughput)+"\n")
		START_TIME = START_TIME+INCREMENT_FACTOR
		END_TIME = END_TIME + INCREMENT_FACTOR	
	t.close()
	c.close()


#subprocess.check_output(NS+" renocbr.tcl "+QUEUE_METHOD,shell=True).strip()
print subprocess.check_output(NS+" renocbr.tcl "+QUEUE_METHOD+" "+CBR_RATE+" "+QUEUE_SIZE,shell=True).strip()
throughputFinder()

if(QUEUE_METHOD == "DropTail"):
	# Combine the throughput results of both TCP variants
	subprocess.check_output("paste TCP_throughput.txt CBR_throughput.txt | awk '{print $1,$2,$4}' > renocbr-tp-droptail.txt",shell=True).strip()
else:
	# Combine the throughput results of both TCP variants
	subprocess.check_output("paste TCP_throughput.txt CBR_throughput.txt | awk '{print $1,$2,$4}' > renocbr-tp-red.txt",shell=True).strip()

# Remove old trash
subprocess.check_output("rm -rf TCP_throughput.txt CBR_throughput.txt",shell=True).strip()
