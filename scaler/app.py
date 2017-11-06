from math import ceil
import os
from time import sleep

from kubernetes import client, config
import requests

LATENCY_SCALING_THRESHOLD = int(os.environ.get('LATENCY_SCALING_THRESHOLD', 50))
QPS_SCALING_THRESHOLD = int(os.environ.get('QPS_SCALING_THRESHOLD', 10000))
MAX_REPLICAS = int(os.environ.get('MAX_REPLICAS', 5))


class InfluxDBConnector(object):
    def __init__(self, host, port, dbname):
        self.host = host
        self.port = port
        self.dbname = dbname

    def _get_url(self, operation):
        return 'http://{}:{}/{}?db={}'.format(self.host, self.port, operation, self.dbname)

    def get(self, query):
        res = requests.get(self._get_url('query') + '&q={}'.format(query))

        if not res.ok:
            raise RuntimeError('An error occurred while getting data from influx: {}'.format(res.text))

        return res.json()

    def post(self, data):
        res = requests.post(url=self._get_url('write'), data=data)

        if not res.ok:
            raise RuntimeError('Could not post to influx: {}'.format(res.text))


def get_influxdb_connector():
    host = os.environ.get('INFLUXDB_HOST', 'influxdb-service')
    port = int(os.environ.get('INFLUXDB_PORT', 8086))
    dbname = os.environ.get('INFLUXDB_DB_NAME', 'metrics')

    return InfluxDBConnector(host, port, dbname)


def get_metrics(influxdb_connector):
    latency_percentile_query = 'SELECT+percentile(%22latency%22%2C+99)+FROM+%22metrics%22+WHERE+time+%3E%3D+now()+-+1m'
    qps_query = 'SELECT+%22qps%22+FROM+%22metrics%22+WHERE+time+%3E%3D+now()+-+1m+limit+1'

    lat_res = influxdb_connector.get(latency_percentile_query)
    qps_res = influxdb_connector.get(qps_query)

    metrics = {
        'qps': qps_res['results'][0]['series'][0]['values'][0][1],
        'latency_99th_percentile': lat_res['results'][0]['series'][0]['values'][0][1],
    }
    return metrics


def scale_pod(api, deployment_name, nb_replicas):
    body = [{"op":"replace","path":"/spec/replicas","value": str(nb_replicas)}]

    return api.patch_namespaced_deployment_scale(name=deployment_name,
                                                 namespace='default',
                                                 body=body)


def get_target_replica_count(metric_value, threshold):
    return min(max(ceil(float(metric_value) / threshold), 1), MAX_REPLICAS)


def main():
    config.load_incluster_config()
    api = client.ExtensionsV1beta1Api()
    influxdb_connector = get_influxdb_connector()

    last_replica_count = 1
    while True:
        metrics = get_metrics(influxdb_connector)
        replica_count = max(get_target_replica_count(metrics['latency_99th_percentile'], LATENCY_SCALING_THRESHOLD),
                            get_target_replica_count(metrics['qps'], QPS_SCALING_THRESHOLD))

        print 'Calculated replica_count:', replica_count

        if replica_count != last_replica_count:
            print 'Scaling pod to:', replica_count
            scale_pod(api, 'memcached-deployment', replica_count)
            influxdb_connector.post('config,replicas={} replicas={}'.format(replica_count, replica_count))
            last_replica_count = replica_count

        sleep(20)


if __name__ == "__main__":
    main()
