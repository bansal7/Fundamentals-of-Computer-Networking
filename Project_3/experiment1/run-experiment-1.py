#!/usr/bin/python
import subprocess
import sys
import os

CBR_START_VALUE = str(0.5)

CURRENT_PATH	= os.getcwd()


# TCP Directory Prefixes
TAHOE   = CURRENT_PATH+"/tahoe"
RENO    = CURRENT_PATH+"/reno"
NEWRENO = CURRENT_PATH+"/newreno"
VEGAS   = CURRENT_PATH+"/vegas"

print "Simulating TCP Tahoe Throughput, Droprate and Latency...",
subprocess.check_output(TAHOE+"/tahoe "+CBR_START_VALUE,shell=True).strip()
print "DONE"

print "Simulating TCP Reno Throughput, Droprate and Latency...",
subprocess.check_output(RENO+"/reno "+CBR_START_VALUE,shell=True).strip()
print "DONE"

print "Simulating TCP Newreno Throughput, Droprate and Latency...",
subprocess.check_output(NEWRENO+"/newreno "+CBR_START_VALUE,shell=True).strip()
print "DONE"

print "Simulating TCP Vegas Throughput, Droprate and Latency...",
subprocess.check_output(VEGAS+"/vegas "+CBR_START_VALUE,shell=True).strip()
print "DONE"


# Combine the TCP results generated

print "Combining TCP Tahoe,Reno,Newreno,Vegas Droprate...",
subprocess.check_output("paste "+TAHOE+"/tahoedroprate.txt \
				"+RENO+"/renodroprate.txt \
				"+NEWRENO+"/newrenodroprate.txt \
				"+VEGAS+"/vegasdroprate.txt \
				| awk '{print $1, $2, $4, $6, $8}' > alldroprate.txt",shell=True)
print "DONE"

print "Combining TCP Tahoe,Reno,Newreno,Vegas Throughput...",
subprocess.check_output("paste "+TAHOE+"/tahoethroughput.txt \
				"+RENO+"/renothroughput.txt \
				"+NEWRENO+"/newrenothroughput.txt \
				"+VEGAS+"/vegasthroughput.txt \
				| awk '{print $1, $2, $4, $6, $8}' > allthroughput.txt",shell=True)
print "DONE"


print "Combining TCP Tahoe,Reno,Newreno,Vegas Latency...",
subprocess.check_output("paste "+TAHOE+"/tahoelatency.txt \
				"+RENO+"/renolatency.txt \
				"+NEWRENO+"/newrenolatency.txt \
				"+VEGAS+"/vegaslatency.txt \
				| awk '{print $1, $2, $4, $6, $8}' > all-latency.txt",shell=True)
print "DONE\n"

print "=============================================================="
print "Performed the following operations successfully"
print "=============================================================="
print "1. Simulated TCP Tahoe Throughput, Droprate and Latency"
print "2. Simulated TCP Reno Throughput, Droprate and Latency"
print "3. Simulated TCP Newreno Throughput, Droprate and Latency"
print "4. Simulated TCP Vegas Throughput, Droprate and Latency"
print "5. Combined TCP Tahoe, Reno, Newreno and Vegas Throughput"
print "6. Combined TCP Tahoe, Reno, Newreno and Vegas Droprate"
print "7. Combined TCP Tahoe, Reno, Newreno and Vegas Latency "
print "=============================================================="
print "JOB COMPLETE"
print "=============================================================="
