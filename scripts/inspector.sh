#!/bin/bash
for i in {1..300}
do
    adb shell su -c netstat -p > netstat/netstat$i
    adb shell su -c tcpdump -v -G 10 -i rmnet_data0 > tcpdump/tcpdump$i
done
