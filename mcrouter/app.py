from copy import deepcopy
import json
from time import sleep

from kubernetes import client, config

MEMCACHED_NAMESPACE = 'default'
MEMCACHED_APP_NAME = 'memcached'

MCROUTER_CONFIG_TEMAPLATE_PATH = '/config_updater/template.conf'
MCROUTER_CONFIG_PATH = '/tmp/mcrouter.conf'

def get_memcached_IPs(api):
    pods = api.list_namespaced_pod(MEMCACHED_NAMESPACE, watch=False)
    mc_ips = [ (pod.status.pod_ip, pod.spec.containers[0].ports[0].container_port)
               for pod in pods.items
               if pod.metadata.labels['app'] == MEMCACHED_APP_NAME ]
    return mc_ips

def read_mcrouter_config_template():
    with open(MCROUTER_CONFIG_TEMAPLATE_PATH, 'r') as tpl_file:
        tpl = tpl_file.read()

    return json.loads(tpl)

def set_memcached_ips_in_config(config_template, memcached_ips):
    servers = [ '%s:%d' % ip for ip in memcached_ips ]
    config = deepcopy(config_template)
    config['pools']['A']['servers'] = servers

    return config

def save_mcrouter_config(config):
    with open(MCROUTER_CONFIG_PATH, 'w') as cfg_file:
        json.dump(config, cfg_file)


if __name__ == "__main__":
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    tpl = read_mcrouter_config_template()

    while True:
        mc_ips = get_memcached_IPs(v1)
        config = set_memcached_ips_in_config(tpl, mc_ips)
        save_mcrouter_config(config)
        sleep(60)

