import random

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
from abstract_thread import AbstractThread, generate_metric_name
from throttling_group import NullThrottlingGroup
from HTTPClient import NVPair

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

    def __init__(self, thread_num, agent_num, request, config,
                 tgroup=NullThrottlingGroup()):
        AbstractThread.__init__(self, thread_num, agent_num, request, config,
                                tgroup)

    def generate_unit(self, tenant_id):
        unit_number = tenant_id % 6
        return self.units_map[unit_number]

    def generate_metric(self, time, tenant_id, metric_id, value):
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
                'metricValue': value,
                'ttlInSeconds': (2 * 24 * 60 * 60),
                'collectionTime': collection_time}

    def generate_payload(self, time, tenant_metric_id_values):
        payload = [self.generate_metric(time, x[0], x[1], x[2]) for x in
                   tenant_metric_id_values]
        return json.dumps(payload)

    def ingest_url(self):
        return "%s/v2.0/tenantId/ingest/multi" % self.config['url']

    def make_request(self, logger, time, tenant_metric_id_values=None):
        if tenant_metric_id_values is None:
            tenant_metric_id_values = []
            for i in xrange(self.config['ingest_batch_size']):
                tenant_id = random.randint(
                    1, self.config['ingest_num_tenants'])
                metric_id = random.randint(
                    1, self.config['ingest_metrics_per_tenant'])
                value = random.randint(0, RAND_MAX)
                tmv = [tenant_id, metric_id, value]
                tenant_metric_id_values.append(tmv)
        payload = self.generate_payload(time, tenant_metric_id_values)
        self.count_request()
        headers = ( NVPair("Content-Type", "application/json"), )
        result = self.request.POST(self.ingest_url(), payload, headers)
        if result.getStatusCode() in [400, 415, 500]:
            logger("Error: status code=" + str(result.getStatusCode()) + " response=" + result.getText())
        return result
