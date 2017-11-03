import json
import os
import time

from flask import Flask
import numpy as np

from pymemcache.client.base import Client


MEMCACHED_HOST = os.environ.get('MEMCACHED_HOST', 'memcached-service')
MEMCACHED_PORT = int(os.environ.get('MEMCACHED_PORT', 11211))

SAMPLE_KEY = 'test-rekonf-2017'
SAMPLE_VALUE = 'pb'

def init_client():
    client = Client((MEMCACHED_HOST, MEMCACHED_PORT))
    client.set(SAMPLE_KEY, SAMPLE_VALUE)
    return client

def get_latency(client):
    """
    Returns lantency (ms)
    """
    st = time.time()
    client.get(SAMPLE_KEY)
    return (time.time() - st) * 1000.0

def get_99th_percentile(client, interval=1000):
    """
    Get 99th percentile from a given measurement interval (ms)
    """
    total_time = 0
    latencies = []
    while total_time < interval:
        latency = get_latency(client)
        total_time += latency
        latencies.append(latency)
    return np.percentile(np.array(latencies), 99)


app = Flask(__name__)
cl = None

@app.route('/metrics')
def get_metrics():
    global cl
    if cl is None:
        cl = init_client()

    response = {
        "99th_percentile": get_99th_percentile(cl),
    }
    return json.dumps(response), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
