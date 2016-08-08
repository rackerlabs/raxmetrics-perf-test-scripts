import random

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
from abstract_thread import AbstractThread, generate_metric_name


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

    def __init__(self, thread_num, agent_num, request, config):
        AbstractThread.__init__(self, thread_num, agent_num, request, config)
        # Initialize the "slice" of the metrics to be sent by this thread

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

    def generate_payload(self, time, tenant_metric_id_pairs):
        payload = [self.generate_metric(time, x[0], x[1]) for x in
                   tenant_metric_id_pairs]
        return json.dumps(payload)

    def ingest_url(self):
        return "%s/v2.0/tenantId/ingest/multi" % self.config['url']

    def make_request(self, logger, time, tenant_metric_id_pairs=None):
        if tenant_metric_id_pairs is None:
            tenant_metric_id_pairs = []
            for i in xrange(self.config['batch_size']):
                tenant_id = random.randint(1, self.config['num_tenants'])
                metric_id = random.randint(1, self.config['metrics_per_tenant'])
                pair = [tenant_id, metric_id]
                tenant_metric_id_pairs.append(pair)
        payload = self.generate_payload(time, tenant_metric_id_pairs)
        result = self.request.POST(self.ingest_url(), payload)
        return result
