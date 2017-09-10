#!/usr/bin/python
import subprocess
import sys
import os

CBR_START_VALUE = str(0.5)
CURRENT_PATH	= os.getcwd()

# TCP Directory Prefixes
NEWRENORENO  = CURRENT_PATH+"/newrenoreno"
NEWRENOVEGAS = CURRENT_PATH+"/newrenovegas"
RENORENO     = CURRENT_PATH+"/renoreno"
VEGASVEGAS   = CURRENT_PATH+"/vegasvegas"

print "Simulating TCP Newreno and Reno Throughput, Droprate and Latency...",
subprocess.check_output(NEWRENORENO+"/newrenoreno "+CBR_START_VALUE,shell=True).strip()
print "DONE"

print "Simulating TCP Newereno and Vegas Throughput, Droprate and Latency...",
subprocess.check_output(NEWRENOVEGAS+"/newrenovegas "+CBR_START_VALUE,shell=True).strip()
print "DONE"

print "Simulating TCP Reno and Reno Throughput, Droprate and Latency...",
subprocess.check_output(RENORENO+"/renoreno "+CBR_START_VALUE,shell=True).strip()
print "DONE"

print "Simulating TCP Vegas and Vegas Throughput, Droprate and Latency...",
subprocess.check_output(VEGASVEGAS+"/vegasvegas "+CBR_START_VALUE,shell=True).strip()
print "DONE"

print "==================================================================="
print "Performed the following operations successfully"
print "==================================================================="
print "1. Simulated TCP Newreno and Reno Throughput, Droprate and Latency"
print "2. Simulated TCP Newreno and Vegas Throughput, Droprate and Latency"
print "3. Simulated TCP Reno and Reno Throughput, Droprate and Latency"
print "4. Simulated TCP Vegas and Vegas Throughput, Droprate and Latency"
print "==================================================================="
print "JOB COMPLETE"
print "==================================================================="
