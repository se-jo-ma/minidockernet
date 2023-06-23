FROM ubuntu:latest

RUN apt update \
&& apt install -y \
        iproute2 \
        git \
        sudo \
        nano \
        snmp \
        snmpd \
        python3 \
        pip \
        bridge-utils \
        net-tools \
        iputils-ping \
        traceroute \
        python3-dev \
        libpq-dev \
&& pip install pyinstaller \
        setuptools \
        waf-build \
        ryu \
        psycopg2 \
&& git clone https://github.com/mininet/mininet \
&& /mininet/util/install.sh -nfv \
&& sudo mv /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.org \
&& echo "rocommunity public" >> /etc/snmp/snmpd.conf \
&& echo "SNMPDOPTS='-LSwd -Lf /dev/null -u Debian-snmp -g Debian-snmp -I -smux,mteTrigger,mteTriggerConf -p /run/snmpd.pid -c /etc/snmp/snmpd.conf'" >> /etc/default/snmpd

COPY ./sanjose.py ./start.sh /root/
COPY ./rsyslog.conf /etc/rsyslog.conf

WORKDIR /root

CMD [ "/bin/sh", "/root/start.sh" ]
