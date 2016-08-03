import random
import time

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
from abstract_thread import AbstractThread, default_config, generate_job_range
from abstract_thread import generate_metrics_tenants, generate_enum_metric_name


class EnumIngestThread(AbstractThread):
    # The list of metric numbers for all threads in this worker
    metrics = []

    @staticmethod
    def _create_metrics(agent_number, config=default_config):
        """ Generate all the metrics for this worker

        The metrics are a list of batches.  Each batch is a list of metrics
        processed by a single metrics ingest request.
        """
        metrics = generate_metrics_tenants(
            config['enum_num_tenants'],
            config['enum_metrics_per_tenant'],
            agent_number,
            config['num_nodes'],
            EnumIngestThread.generate_metrics_for_tenant)

        return EnumIngestThread.divide_metrics_into_batches(
            metrics,
            config['batch_size'])

    @classmethod
    def create_metrics(cls, agent_number, config=default_config):
        """ Generate all the metrics for this worker

        The metrics are a list of batches.  Each batch is a list of metrics
        processed by a single metrics ingest request.
        """
        cls.metrics = cls._create_metrics(agent_number, config)

    @classmethod
    def num_threads(cls, config=default_config):
        return config['enum_ingest_concurrency']

    @staticmethod
    def generate_metrics_for_tenant(tenant_id, metrics_per_tenant):
        l = []
        for x in range(metrics_per_tenant):
            l.append([tenant_id, x])
        return l

    @staticmethod
    def divide_metrics_into_batches(metrics, batch_size):
        b = []
        for i in range(0, len(metrics), batch_size):
            b.append(metrics[i:i + batch_size])
        return b

    def __init__(self, thread_num, agent_num, request, config=None):
        AbstractThread.__init__(self, thread_num, agent_num, config)
        # Initialize the "slice" of the metrics to be sent by this thread
        start, end = generate_job_range(len(self.metrics),
                                        self.num_threads(), thread_num)
        self.slice = self.metrics[start:end]
        self.request = request

    def generate_enum_suffix(self):
        return "_" + str(random.randint(0, self.config['enum_num_values']))

    def generate_enum_metric(self, time, tenant_id, metric_id):
        return {'tenantId': str(tenant_id),
                'timestamp': time,
                'enums': [{'name': generate_enum_metric_name(metric_id),
                           'value': 'e_g_' + str(
                               metric_id) + self.generate_enum_suffix()}]
                }

    def generate_payload(self, time, batch):
        payload = map(lambda x: self.generate_enum_metric(time, *x), batch)
        return json.dumps(payload)

    def ingest_url(self):
        return "%s/v2.0/tenantId/ingest/aggregated/multi" % self.config[
            'url']

    def make_request(self, logger):
        if len(self.slice) == 0:
            logger("Warning: no work for current thread")
            self.sleep(1000000)
            return None
        self.check_position(logger, len(self.slice))
        batch = self.get_next_item()
        payload = self.generate_payload(int(self.time()), batch)
        result = self.request.POST(self.ingest_url(), payload)
        return result
