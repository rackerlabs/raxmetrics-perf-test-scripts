import random

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
from abstract_thread import AbstractThread, generate_job_range
from abstract_thread import generate_metrics_tenants


class EnumIngestThread(AbstractThread):
    # The list of metric numbers for all threads in this worker
    metrics = []

    @staticmethod
    def _create_metrics(agent_number, config):
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
    def num_threads(cls, config):
        return config['enum_ingest_weight']

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

    # TODO: Add enum prefix to config
    @staticmethod
    def generate_enum_metric_name(metric_id, config):
        return "enum_grinder_" + config['name_fmt'] % metric_id

    def __init__(self, thread_num, agent_num, request, config):
        AbstractThread.__init__(self, thread_num, agent_num, request, config)
        # Initialize the "slice" of the metrics to be sent by this thread
        self.metrics = self._create_metrics(agent_num, config)
        start, end = generate_job_range(len(self.metrics),
                                        self.num_threads(self.config),
                                        thread_num)
        self.slice = self.metrics[start:end]

    def generate_enum_suffix(self):
        return "_" + str(random.randint(0, self.config['enum_num_values']))

    def generate_enum_metric(self, time, tenant_id, metric_id):
        return {'tenantId': str(tenant_id),
                'timestamp': time,
                'enums': [{'name': self.generate_enum_metric_name(metric_id,
                                                                  self.config),
                           'value': 'e_g_' + str(
                               metric_id) + self.generate_enum_suffix()}]
                }

    def generate_payload(self, time, batch):
        payload = map(lambda x: self.generate_enum_metric(time, *x), batch)
        return json.dumps(payload)

    def ingest_url(self):
        return "%s/v2.0/tenantId/ingest/aggregated/multi" % self.config[
            'url']

    def make_request(self, logger, time):
        if len(self.slice) == 0:
            logger("Warning: no work for current thread")
            return None
        self.check_position(logger, len(self.slice))
        batch = self.get_next_item()
        payload = self.generate_payload(int(self.time()), batch)
        result = self.request.POST(self.ingest_url(), payload)
        return result
