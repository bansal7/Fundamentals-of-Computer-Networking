#============ delay-e2e.awk =========
BEGIN {
  src="4.0"; dst="5.0";
  num_samples = 0;
  total_delay = 0;
}
/^\+/&&$9==src&&$10==dst {
    t_arr[$12] = $2;
#	print "t_arr[$12] = " t_arr[$12]
};

/^r/&&$9==src&&$10==dst{
    if (t_arr[$12] > 0) {
      	num_samples++;
      	delay = $2 - t_arr[$12];
    	total_delay += delay;
    };
};

END{
	avg_delay = total_delay/num_samples;

#  print "Average end-to-end transmission delay is " avg_delay  " seconds";
#  print "Measurement details:"; 
#  print "  - Since packets are created from the address " src;
#  print "  - Until the packets are destroyed at the address " dst;

#  Since the script counts a sample as movement of the same packet between 
#  different nodes, every packet's 3 movements are counted as samples
#  Hence the overall delay would be for every packet movement between 2 nodes
#  But we are interested in knowing the average delay for 1 packet to reach
#  a destination node from source node
#  Since every packet is counted thrice in total number of samples, we have to
#  multiply the final average by 3 to get the average delay to move from
#  source to destination(NOTE: This is different from node to node delay)

   print (avg_delay * 3)
};
