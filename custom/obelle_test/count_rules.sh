#!/bin/bash

total_rule=$((5 * $2 + 13))
echo "check if dp has $total_rule rules properly"
for (( i=1; i<$1+1; i++ )) do
	rule_num=$(ovs-ofctl dump-flows s$i -O openflow13 | wc -l) 
	if [[ $rule_num -lt $total_rule ]]
	then
		echo "s$i has only $rule_num rules"
	fi
done
