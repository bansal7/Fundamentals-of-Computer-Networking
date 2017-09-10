# Throughput calculator for TCP/CBR
# How to run this file: 
#    awk -f tp.awk starttime=<STARTTIME_REQUIRED> endtime=<ENDTIME_REQUIRED> toNode=<TCP(3) or CBR(5)> renocbr.tr

BEGIN {
	fromNode=2; 
#	toNode=5;
	lineCount = 0;totalBits = 0;
	endtime=endtime;
	no_of_records_matched = 0;
}

/^r/&&$3==fromNode&&$4==toNode&&$2>starttime&&$2<endtime{
	totalBits += 8*$6;
	no_of_records_matched = no_of_records_matched + 1
	if ( lineCount==0 ) {
		timeBegin = $2; 
		lineCount++;
	} else {
		timeEnd = $2;
	};
};
END{
	if(no_of_records_matched == 0){
		print no_of_records_matched;	
	}
	else if(no_of_records_matched == 1){
		print totalBits/1e3; 
	}
	else{
		duration = timeEnd-timeBegin;
		print totalBits/duration/1e3; 
	}
};
