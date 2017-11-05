import json
import os
import time

import requests

from pymemcache.client.base import Client


MCROUTER_HOST = os.environ.get('MCROUTER_HOST', 'mcrouter-service')
MCROUTER_PORT = int(os.environ.get('MCROUTER_PORT', 5000))

INFLUXDB_HOST = os.environ.get('INFLUXDB_HOST', 'influxdb-service')
INFLUXDB_PORT = int(os.environ.get('INFLUXDB_PORT', 8086))
INFLUXDB_DBNAME = os.environ.get('INFLUXDB_DBNAME', 'metrics')

SAMPLE_KEY = 'test-rekonf-2017'
SAMPLE_VALUE = 'pb'


def init_client():
    client = Client((MCROUTER_HOST, MCROUTER_PORT))
    client.set(SAMPLE_KEY, SAMPLE_VALUE)
    return client


def get_latency(client):
    """
    Returns lantency (ms)
    """
    st = time.time()
    client.get(SAMPLE_KEY)
    return (time.time() - st) * 1000.0


last_nb_get_cmd = None
prev_time = None


def get_qps(client):
    """
    Return queries per second
    """
    global last_nb_get_cmd
    global prev_time

    st = client.stats()
    nb_cmd_get = st['cmd_get_count']

    if last_nb_get_cmd is None:
        last_nb_get_cmd = nb_cmd_get
        prev_time = time.time()
        return 0

    curr_time = time.time()
    qps = (nb_cmd_get - last_nb_get_cmd) / (curr_time - prev_time)

    last_nb_get_cmd = nb_cmd_get
    prev_time = curr_time

    return qps


class InfluxDBLogger(object):
    def __init__(self, host, port, dbname):
        self.host = host
        self.port = port
        self.dbname = dbname

    def _get_url(self):
        return 'http://{}:{}/write?db={}'.format(self.host, self.port, self.dbname)

    def post(self, data):
        res = requests.post(url=self._get_url(), data=data)
        if not res.ok:
            raise RuntimeError('Could not post to influx: {}'.format(res.text))


def get_influxdb_logger():
    return InfluxDBLogger(INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_DBNAME)


if __name__ == "__main__":
    cl = init_client()
    influx_logger = get_influxdb_logger()
    while True:
        latency = get_latency(cl)
        qps = get_qps(cl)

        influx_logger.post(
            data='metrics,collector=1 latency={},qps={}'.format(
                latency,
                qps
            )
        )

        time.sleep(1)

