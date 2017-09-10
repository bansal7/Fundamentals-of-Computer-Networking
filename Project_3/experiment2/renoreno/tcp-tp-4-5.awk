
BEGIN {
	src=4.0; dst=5.0;
	fromNode=2; toNode=5;
	lineCount = 0;totalBits = 0;
}

/^r/&&$3==fromNode&&$4==toNode&&$9==src&&$10==dst{
	totalBits += 8*$6;
	if ( lineCount==0 ) {
		timeBegin = $2; 
		lineCount++;
	} else {
		timeEnd = $2;
	};
};
END{
	duration = timeEnd-timeBegin;
#	print "Number of records is " NR;
#	print "Output: ";
#	print "Transmission: N" fromNode "->N" toNode; 
#	print "  - Total transmitted bits = " totalBits " bits";
#	print "  - duration = " duration " s"; 
#	print "  - Thoughput = "  totalBits/duration/1e3 " kbps."; 
#	print "Throughput = "  totalBits/duration/1e3 " kbps"; 
	print totalBits/duration/1e3; 
};
