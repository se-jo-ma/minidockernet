FROM ubuntu:latest

RUN apt update \
&& apt install -y \
        iproute2 \
        git \
        sudo \
        rsyslog \
        snmp \
        snmpd \
        python3 \
        pip \
        bridge-utils \
        net-tools \
        iputils-ping \
        traceroute \
&& pip install pyinstaller setuptools waf-build ryu \
&& git clone https://github.com/mininet/mininet

COPY ./sanjose.py /root/sanjose.py
COPY ./start.sh /root/start.sh

#Needs to be run on the host machine after spin up. Put into sh file?
CMD [ "/bin/sh" ]