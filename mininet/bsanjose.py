from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.nodelib import LinuxBridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info

# Setting global data
SNMP_START_CMD = '/usr/sbin/snmpd -Lsd -Lf /dev/null -u Debian-snmp -I -smux -p /var/run/snmpd.pid -c /etc/snmp/snmpd.conf'
SNMP_WALK_CMD = ' snmpwalk -v 1 -c public -O e '
SNMP_SYSLOG = ' snmpwalk -L s '
SNMP_WALK_OUT = 'dump.out'

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

class NetworkTopo( Topo ):
    def build(self):
        #Routers
        rtg1 = self.addNode( 'rtg1', cls=LinuxRouter, ip='10.0.51.1/24')
        # rtw1 = self.addNode( 'rtw1', cls=LinuxRouter, ip='10.0.0.11/24' ) # will need later
        # rtw2 = self.addNode( 'rtw2', cls=LinuxRouter, ip='10.0.0.12/24' ) # will need later

        #Switches
        swg1 = self.addSwitch( 'swg1' )
        swg2 = self.addSwitch( 'swg2' )

        #Links for Routers and Switches
        self.addLink( swg1, rtg1, intfName2='rtg1-eth1',
                      params2={ 'ip' : '10.0.51.1/24' } )  # for clarity
        self.addLink( swg2, rtg1, intfName2='rtg1-eth2',
                      params2={ 'ip' : '12.0.52.1/12' } )
        #Hosts
        ssd1 = self.addHost( 'ssd1', ip='10.0.51.110/24', defaultRoute='via 10.0.51.1')
        ssd2 = self.addHost( 'ssd2', ip='12.0.52.100/12', defaultRoute='via 12.0.52.1')
        svcg1 = self.addHost( 'svcg1', ip='10.0.51.120/24', defaultRoute='via 10.0.51.1')
        svcg2 = self.addHost( 'svcg2', ip='12.0.52.120/12', defaultRoute='via 12.0.52.1')
        svpg1 = self.addHost( 'svpg1', ip='10.0.51.130/24', defaultRoute='via 10.0.51.1')
        svpg2 = self.addHost( 'svpg2', ip='12.0.52.130/12', defaultRoute='via 12.0.52.1')

        #Links for Host and Switches
        for h,s in [(ssd1,swg1),(ssd2,swg2),(svcg1,swg1),(svcg2,swg2),(svpg1,swg1),(svpg2, swg2)]:
            self.addLink(h,s)
        
def setup_snmp(network,topology):
    net = network
    topo = topology
    for host in topo.nodes():
        # print(host)
        net[f'{host}'].cmd(SNMP_START_CMD)
        # net[f'{host}'].cmd(f'{SNMP_SYSLOG} syslog')

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( switch=LinuxBridge, topo=topo )
    net.start()
    info( '*** Routing Table on Router:\n' )    
    print(net[ 'rtg1' ].cmd( 'route' ))   
    net['c0'].cmd(SNMP_START_CMD)
    setup_snmp(net,topo)
    CLI( net )
    net.stop()

topo = {'sj': (lambda: NetworkTopo())}
if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
