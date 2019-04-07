#!/bin/bash
adb shell su -c tcpdump -v -i rmnet_data0 > tcpdump/tcpdump
