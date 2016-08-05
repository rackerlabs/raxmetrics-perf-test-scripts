import random

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
from abstract_thread import AbstractThread, generate_job_range
from abstract_thread import generate_metrics_tenants, generate_metric_name


RAND_MAX = 982374239


class IngestThread(AbstractThread):

    units_map = {
        0: 'minutes',
        1: 'hours',
        2: 'days',
        3: 'months',
        4: 'years',
        5: 'decades'
    }

    # The list of metric numbers for all threads in this worker
    metrics = []

    @staticmethod
    def _create_metrics(agent_number, config):
        """ Generate all the metrics for this worker

        The metrics are a list of batches.  Each batch is a list of metrics
        processed by a single metrics ingest request.
        """
        metrics = generate_metrics_tenants(
            config['num_tenants'],
            config['metrics_per_tenant'],
            agent_number, config['num_nodes'],
            IngestThread.generate_metrics_for_tenant)

        return IngestThread.divide_metrics_into_batches(
            metrics, config['batch_size'])

    @classmethod
    def create_metrics(cls, agent_number, config):
        """ Generate all the metrics for this worker

        The metrics are a list of batches.  Each batch is a list of metrics
        processed by a single metrics ingest request.
        """
        cls.metrics = cls._create_metrics(agent_number, config)

    @classmethod
    def num_threads(cls, config):
        return config['ingest_concurrency']

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

    def __init__(self, thread_num, agent_num, request, config):
        AbstractThread.__init__(self, thread_num, agent_num, config)
        # Initialize the "slice" of the metrics to be sent by this thread
        start, end = generate_job_range(len(self.metrics),
                                        self.num_threads(self.config), thread_num)
        self.slice = self.metrics[start:end]
        self.request = request

    def generate_unit(self, tenant_id):
        unit_number = tenant_id % 6
        return self.units_map[unit_number]

    def generate_metric(self, time, tenant_id, metric_id):
        ingest_delay_millis = self.config['ingest_delay_millis']

        collection_time = time
        # all even tenants have possible delayed metrics
        if len(ingest_delay_millis) > 0 and tenant_id % 2 == 0:
            collection_times = [time - long(delay) for delay in
                                ingest_delay_millis.split(",")]
            collection_time = random.choice(collection_times)

        return {'tenantId': str(tenant_id),
                'metricName': generate_metric_name(metric_id, self.config),
                'unit': self.generate_unit(tenant_id),
                'metricValue': random.randint(0, RAND_MAX),
                'ttlInSeconds': (2 * 24 * 60 * 60),
                'collectionTime': collection_time}

    def generate_payload(self, time, batch):
        payload = map(lambda x: self.generate_metric(time, *x), batch)
        return json.dumps(payload)

    def ingest_url(self):
        return "%s/v2.0/tenantId/ingest/multi" % self.config['url']

    def make_request(self, logger, time):
        if len(self.slice) == 0:
            logger("Warning: no work for current thread")
            self.sleep(1000000)
            return None
        self.check_position(logger, len(self.slice))
        batch = self.get_next_item()
        payload = self.generate_payload(int(self.time()), batch)
        result = self.request.POST(self.ingest_url(), payload)
        return result
