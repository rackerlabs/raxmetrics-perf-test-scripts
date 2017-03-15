import random

from raw_ingest_counter import NullIngestCounter

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
from abstract_generator import AbstractGenerator, generate_metric_name
from throttling_group import NullThrottlingGroup

try:
    from HTTPClient import NVPair
except ImportError:
    from nvpair import NVPair


RAND_MAX = 982374239


def int_from_tenant(tenant_id):
    if isinstance(tenant_id, basestring):
        try:
            return int(tenant_id)
        except (TypeError, ValueError):
            pass
    return hash(tenant_id)


class IngestGenerator(AbstractGenerator):

    units_map = {
        0: 'minutes',
        1: 'hours',
        2: 'days',
        3: 'months',
        4: 'years',
        5: 'decades'
    }

    raw_ingest_counter = NullIngestCounter()

    def generate_unit(self, tenant_id):
        tenant_id = int_from_tenant(tenant_id)
        unit_number = tenant_id % 6
        return self.units_map[unit_number]

    def generate_metric(self, time, tenant_id, metric_id, value):
        ingest_delay_millis = self.config['ingest_delay_millis']

        collection_time = time
        # all even tenants have possible delayed metrics
        tenant_int = int_from_tenant(tenant_id)
        if len(ingest_delay_millis) > 0:
            collection_times = [time - long(delay) for delay in
                                ingest_delay_millis.split(",")]
            collection_time = random.choice(collection_times)

        return {'tenantId': str(tenant_id),
                'metricName': generate_metric_name(metric_id, self.config),
                'unit': self.generate_unit(tenant_int),
                'metricValue': value,
                'ttlInSeconds': (2 * 24 * 60 * 60),
                'collectionTime': collection_time}

    def generate_payload(self, time, tenant_metric_id_values):
        payload = [self.generate_metric(time, x[0], x[1], x[2]) for x in
                   tenant_metric_id_values]
        return json.dumps(payload)

    def ingest_url(self, tenantId=None):
        if tenantId is None:
            tenantId = self.user.get_tenant_id()
        return "%s/v2.0/%s/ingest/multi" % (self.config['url'], str(tenantId))

    def make_request(self, logger, time, tenant_metric_id_values=None):
        if tenant_metric_id_values is None:
            tenant_metric_id_values = []
            for i in xrange(self.config['ingest_batch_size']):
                tenant_id = self.user.get_tenant_id()
                metric_id = random.randint(
                    1, self.config['ingest_metrics_per_tenant'])
                value = random.randint(0, RAND_MAX)
                tmv = [tenant_id, metric_id, value]
                tenant_metric_id_values.append(tmv)
        payload = self.generate_payload(time, tenant_metric_id_values)
        headers = ( NVPair("Content-Type", "application/json"), )
        url = self.ingest_url()
        result = self.request.POST(url, payload, headers)
        if result.getStatusCode() >= 400:
            logger("IngestGenerator Error: status code=" + str(result.getStatusCode()) + " response=" + result.getText())
        if 200 <= result.getStatusCode() < 300:
            self.count_raw_metrics(len(tenant_metric_id_values))
        return result

    def count_raw_metrics(self, n):
        self.raw_ingest_counter.count(n)
