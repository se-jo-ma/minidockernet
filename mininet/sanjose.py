from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.nodelib import LinuxBridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info


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
        swg1 = self.addSwitch( 'swg1' )
        swg2 = self.addSwitch( 'swg2' )
        
        rtg1 = self.addNode( 'rtg1', cls=LinuxRouter, ip='10.0.51.16/24' )
        rtw1 = self.addNode( 'rtw1', cls=LinuxRouter, ip='10.0.0.11/24' )
        rtw2 = self.addNode( 'rtw2', cls=LinuxRouter, ip='10.0.0.12/24' )
                
        ssd1 = self.addHost( 'ssd1', ip='10.0.54.133')
        ssd2 = self.addHost( 'ssd2', ip='10.0.54.134')
        svcg1 = self.addHost( 'svcg1', ip='10.0.54.129')
        svcg2 = self.addHost( 'svcg2', ip='10.0.54.130')
        svpg1 = self.addHost( 'svpg1', ip='10.0.54.131')
        svpg2 = self.addHost( 'svpg2', ip='10.0.54.132')

        self.addLink( swg1, rtg1, intfName2='rtg1-eth1',
                      params2={ 'ip' : '10.0.51.17/24' } )  # for clarity
        self.addLink( swg2, rtg1, intfName2='rtg1-eth2',
                      params2={ 'ip' : '10.0.51.18/24' } )

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )  # controller is used by s1-s3
    net.start()
    # info( '*** Routing Table on Router:\n' )
    print(net[ 'rtg1' ].cmd( 'route' ))
    CLI( net )
    net.stop()

topo = {'sj': (lambda: NetworkTopo())}
if __name__ == '__main__':
    # setLogLevel( 'info' )
    run()