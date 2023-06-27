from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, Host
from mininet.nodelib import LinuxBridge
from mininet.cli import CLI
from mininet.log import setLogLevel, info, lg



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
        swg1 = self.addSwitch( 'swg1', ip='10.0.51.17/24')
        swg2 = self.addSwitch('swg2', ip='10.0.51.18/24')
        
        
        rtg1 = self.addNode( 'rtg1', cls=LinuxRouter, ip='10.0.54.16/24' )
        # rtw1 = self.addNode( 'rtw1', cls=LinuxRouter, ip='10.0.0.11/24' )
        # rtw2 = self.addNode( 'rtw2', cls=LinuxRouter, ip='10.0.0.12/24' )
                
        ssd1 = self.addHost( 'ssd1', cls=Host, ip='10.0.54.133/24',defaultRoute='via 10.0.54.16')
        ssd2 = self.addHost( 'ssd2',cls=Host, ip='10.0.54.134/24',defaultRoute='via 10.0.54.16')
        svcg1 = self.addHost( 'svcg1',cls=Host, ip='10.0.54.129/24',defaultRoute='via 10.0.54.16')
        svcg2 = self.addHost( 'svcg2',cls=Host, ip='10.0.54.130/24',defaultRoute='via 10.0.54.16')
        svpg1 = self.addHost( 'svpg1',cls=Host, ip='10.0.54.131/24',defaultRoute='via 10.0.54.16')
        svpg2 = self.addHost( 'svpg2',cls=Host, ip='10.0.54.132/24',defaultRoute='via 10.0.51.16')

        self.addLink( swg1, rtg1, intfName2='rtg1-eth1',
                      params2={ 'ip' : '10.0.54.16/24' } )  # for clarity
        self.addLink( swg2, rtg1, intfName2='rtg1-seth1',
                      params2={ 'ip' : '10.0.54.17/24' } )
        self.addLink(swg1,swg2)
        
        
        #Links for Host and Switches
        for h,s in [(ssd1,swg1),(ssd2,swg2),(svcg1,swg1),(svcg2,swg2),(svpg1,swg1),(svpg2, swg2)]:
            self.addLink(h,s)

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( switch=LinuxBridge, topo=topo )  # controller is used by s1-s3
    net.start()
    # info( '*** Routing Table on Router:\n' )
    print(net[ 'rtg1' ].cmd( 'route' ))
    CLI( net )
    net.stop()

topo = {'sj': (lambda: NetworkTopo())}
if __name__ == '__main__':
    setLogLevel( 'info' )
    lg.setLogLevel('info')
    
    run()
