#!/bin/bash
echo 'Starting SNMP'
/etc/init.d/snmpd restart

echo 'Setting up RSyslog'
sudo DEBIAN_FRONTEND=noninteractive apt install -y expect
expect << EOF
set timeout 20
spawn sudo apt install -y rsyslog
expect {
    -re {.*(Y/I/N/O/D/Z).*} {
        send "\r"
        exp_continue
    }
    eof
}
spawn sudo apt install -y rsyslog-pgsql
expect {
    -re {Configure database for rsyslog-pgsql with dbconfig-common?.*} {
        send "no\r"
        exp_continue
    }
    eof
}
EOF
apt install -y rsyslog-relp
apt install -y rsyslog-snmp

sudo apt remove expect -y
rsyslogd

echo 'Spinning up Linux Bridge'
sudo brctl addbr br02
sudo brctl addif br0 eth0
sudo ifconfig br0 up
sudo ip link set br0 up
sudo brctl show
echo 'Built Linux Bridge'

echo Starting Mininet Project
python3 /root/bsanjose.py

# Catch the shell if need be
echo Catching the shell
/bin/sh
