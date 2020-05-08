#!/bin/bash
ip=10.200.101.
for n in `seq 1 254`
do
ping -c 2 $ip$n &> /tmp/day11.log
  if (($?==0))
  then
  echo "$ip$n 在线"
  else
  echo "$ip$n 不在线"
  fi
done
