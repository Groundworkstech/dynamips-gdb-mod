#!/bin/bash
~/projects/cisco/tools/dynamips-0.2.8-RC2/dynamips -P 1700 -t 1760 -r 100 -T 1234 -s 0:0:linux_eth:eth1 ../C1700-EN.BIN
#~/projects/cisco/tools/dynamips-0.2.8-RC2/dynamips -P 1700 -t 1760 -r 100 -s 0:0:gen_eth:eth1 ../C1700-EN.BIN
#~/projects/cisco/tools/dynamips-0.2.8-RC2/dynamips -P 1700 -t 1760 -r 100 -s 0:0:gen_eth:vmnet1 ../C1700-EN.BIN
