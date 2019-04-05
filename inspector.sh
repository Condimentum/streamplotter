#!/bin/bash
for i in {1..300}
do
    adb shell su -c netstat -p > netstat$i
    timeout 10 adb shell su -c tcpdump -v -i rmnet_data0 > tcpdump$i
done
