#!/bin/bash

if [ `whoami` != 'root' ]
then
	echo '请以root身份运行'
	exit 1
fi

# SS服务器
SSSERVER_HOST=
SSSERVER_PORT=
# 本机监听端口
LOCALHOST_PORT=
# 本机IP
LOCALHOST_IP=
# rename
SH=$SSSERVER_HOST
SP=$SSSERVER_PORT
LP=$LOCALHOST_PORT
LI=$LOCALHOST_IP

iptables -t nat -A PREROUTING -p tcp --dport $LP -j DNAT --to-destination $SH:$SP
iptables -t nat -A PREROUTING -p udp --dport $LP -j DNAT --to-destination $SH:$SP

iptables -t nat -A POSTROUTING -p tcp -d $SH --dport $SP -j SNAT --to-source $LI
iptables -t nat -A POSTROUTING -p udp -d $SH --dport $SP -j SNAT --to-source $LI
