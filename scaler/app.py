import json
from math import ceil
import os
from shlex import split
from subprocess import call
from time import sleep

import requests

SCALING_THRESHOLD = os.environ.get('SCALING_THRESHOLD', 2)
MAX_REPLICAS = os.environ.get('MAX_REPLICAS', 5)
METRICS_HOST = os.environ.get('METRICS_HOST', 'memcached-metrics-service')
METRICS_PORT = int(os.environ.get('METRICS_PORT', 5000))

def set_auth_token():
    TOKEN_FILE = '/var/run/secrets/kubernetes.io/serviceaccount/token'
    with open(TOKEN_FILE, 'r') as tokenf:
        os.environ['MY_TOKEN'] = tokenf.read()

def get_metrics():
    res = requests.get(
            'http://{}:{}/metrics'.format(
                METRICS_HOST,
                METRICS_PORT
            )
        )

    if not res.ok:
        raise RuntimeError('Couldn\'t get answer from metrics-service')

    return res.json()

def get_target_replica_count(metric_value, threshold):
    return min(max(ceil(float(metric_value) / threshold), 1), MAX_REPLICAS)

def scale_pod(nb_replicas):
    print 'Scaling to:', nb_replicas
    cmd = ('curl -X PATCH -sSk'
          ' -d \'[{"op":"replace","path":"/spec/replicas","value":"' + str(nb_replicas) + '"}]\''
          ' -H \"Authorization: Bearer ' + str(os.environ.get('MY_TOKEN')) + '\"'
          ' -H \"Accept: application/json\"'
          ' -H \"Content-Type: application/json-patch+json\"'
          ' https://kubernetes:443/apis/extensions/v1beta1/namespaces/default/deployments/memcached-deployment/scale')
    print 'CMD = ', cmd
    call(split(cmd))

if __name__ == "__main__":
    set_auth_token()

    last_replica_count = 1
    while True:
        metrics = get_metrics()
        percentile_99th = metrics['99th_percentile']

        replica_count = get_target_replica_count(percentile_99th,
                                                 SCALING_THRESHOLD)

        print 'Calculated replica_count', replica_count

        if replica_count != last_replica_count:
            scale_pod(replica_count)
            last_replica_count = replica_count

        sleep(20)

