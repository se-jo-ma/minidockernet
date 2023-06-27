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
        self.images_path = os.path.join(FILE_DIR, "docker_images")
        self.prune()

    def prune(self) -> None:
        self.client.images.prune()
        self.client.containers.prune()
        
        self.client.volumes.prune()
  
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
            'network': 'project_net'
        }
        c = self.client.containers.run(**container_config)
        return c
    
   
    def build_db_container(self):
        """This should only be used for testing purposes.
        This builds a docker container with a Postgres database running.
        For testing this should be used in conjunction with a script that
        fills the database with relevant tables and data.

        Returns:
            docker.container: docker container with Postgres database running.
        """
        # image = CLIENT.images.build(path=str(os.path.join(FILE_DIR,"DB")), tag='database', rm=True)[0]
        container_config = {
            'name': 'database',
            'network': 'project_net',
            'image': 'postgres:latest',
            'auto_remove': False,
            'detach': True,
            'tty': True,
            'stdin_open': True,
            'environment': ['POSTGRES_DB=e2e','POSTGRES_PASSWORD=postgres'],
            
        }
        return self.client.containers.run(**container_config)
    
    def build_network(self):
        self.client.networks.prune()
        sleep(1)
        self.client.networks.create(
                                        'project_net', 
                                        driver='bridge', 
                                        attachable=True, 
                                        check_duplicate=True
                                        )


def build_mininet():
    client = DockerClient()
    client.build_network()
    client.build_db_container()
    sleep(5)
    client.build_mininet_container()
    

def main():
    build_mininet()
 
if __name__ == "__main__":
    exit(main())
