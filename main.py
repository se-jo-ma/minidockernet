# standard library imports
import json
import os
from io import BytesIO
from typing import Callable, Any
from pathlib import Path
from time import sleep

# third party imports
import docker
from docker.types import LogConfig 

FILE_DIR = Path(__file__).parent
LC = LogConfig(type=LogConfig.types.JSON)


class DockerClient:
    def __init__(self):
        self.client = docker.from_env()
        self.images = self.get_images()
        self.networks = self.get_networks()
        self.containers = self.get_containers()
        self.images_path = os.path.join(FILE_DIR, "docker_images")
        self.prune()

    def prune(self) -> None:
        self.client.images.prune()
        self.client.containers.prune()
        self.client.networks.prune()
        self.client.volumes.prune()
        
    def build_image(self, img_name):
        with open(os.path.join(self.images_path, img_name), 'rb') as f:
            df_content = BytesIO(f.read())
        print(f"Building image: {img_name}")
        img_name = img_name.lower()
        image, build_logs = self.client.images.build(path=str(FILE_DIR), fileobj=df_content, tag=img_name, rm=True)
        
        self.images[img_name] = image
        return image
    
    def build_container(self, device):
        name = device.get('name') or 'default'
        img_name = device.get('type') or 'AlpineBase'
        print(f"Building container: {name}")
        container_config = {
            'name': name,
            'log_config': LC,
            'auto_remove': True,
            'detach': True,
            'stdin_open': True,
            'tty': True,            
        }
        if img_name in ['Switch', 'Router']:
            container_config['privileged'] = True
        image = self.build_image(img_name)
        container_config['image'] = image.id
        self.containers[name] = c = self.client.containers.run(**container_config)
        c.exec_run(f"ip addr {device.get('ip')} dev eth0")
        return c
    
    def create_network(self, name, driver='bridge'):
        print(f"Creating network: {name}")
        # ipam_pool = docker.types.IPAMPool(subnet='10.0.0.0/16')
        # ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
        net = self.networks.get(name) or self.client.networks.create(name, driver, attachable=True, check_duplicate=True)
        self.networks[name] = net
        return net
    
    def get_containers(self):
        containers = {}
        for c in self.client.containers.list():
            containers.update({c.name: c})
        return containers
    
    def get_networks(self):
        networks = {}
        for n in self.client.networks.list():
            networks.update({n.name: n})
        return networks
    
    def get_images(self):
        images = {}
        for img in self.client.images.list():
            for tag in img.tags:
                tag = tag.split(':')[0]
                images.update({tag: img})
        return images
    def build_mininet_container(self):
        img = self.client.images.build(path=str(os.path.join(FILE_DIR,'mininet')), tag='mininet', rm=True)[0]
        container_config = {
            'name': 'mininet1',
            'image': img.id,
            'log_config': LC,
            'auto_remove': False,
            'detach': True,
            'stdin_open': True,
            'tty': True,
            'privileged': True,
        }
        self.containers['mininet'] = c = self.client.containers.run(**container_config)
        return c
    
def build_network(net_config, client: DockerClient = DockerClient()):
    devices = net_config.get('network_params').get('devices')
    switches = [device for device in devices.values() if device.get('type') == 'Switch']
    routers = [device for device in devices.values() if device.get('type') == 'Router']
    networks = {}
    for device in devices.values():
        c = client.containers.get(device.get('name')) or client.build_container(device)
    for switch in switches:
        networks[switch['name']] = net = client.create_network(f"{switch.get('name')}_network")
        c = client.containers.get(switch.get('name'))
        links = [(c.id, client.containers.get(link).id) for link in switch.get('links')]
        net.connect(c, links=links)
    for router in routers:
        networks[router['name']] = net = client.create_network(f"{router.get('name')}_network")
        c = client.containers.get(router.get('name'))
        links = [(c.id, client.containers.get(link).id) for link in router.get('links')]
        net.connect(c, links=links)
    """
    for device in devices.values():
        c = client.containers.get(device.get('name'))
        if not device.get('links') or not device.get('ip'):
            continue
        for link in device.get('links'):
            if networks.get(link):
                print(f"Connecting {c.name} to {link}")
                networks[link].connect(c)
            else:
                print(f"Network {link} not found")
    """
    for network in networks.values():
        net_cons = client.client.api.inspect_network(network.id)['Containers']
        print(f"Network: {network.name}")
        for c in net_cons.values():
            print(c['Name'], c['IPv4Address'])


def build_mininet():
    client = DockerClient()
    client.build_mininet_container()

def main():
    build_mininet()
    # client = DockerClient()
    # for net in os.listdir(os.path.join(FILE_DIR, "network-configs")):
    #     net_config = json.load(open(os.path.join(FILE_DIR, "network-configs", net), 'r'))
    #     build_network(net_config, client)



if __name__ == "__main__":
    exit(main())