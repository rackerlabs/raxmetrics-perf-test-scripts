
import random

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


class AnnotationsIngestGenerator(AbstractGenerator):

    def generate_annotation(self, time, metric_id):
        metric_name = generate_metric_name(metric_id, self.config)
        return {'what': 'annotation ' + metric_name,
                'when': time,
                'tags': 'tag',
                'data': 'data'}

    def generate_payload(self, time, metric_id):
        payload = self.generate_annotation(time, metric_id)
        return json.dumps(payload)

    def ingest_url(self, tenant_id=None):
        if tenant_id is None:
            if self.user.is_real_user():
                tenant_id = self.user.get_tenant_id()
            else:
                tenant_id = random.randint(0, self.config['annotations_num_tenants'])
        return "%s/v2.0/%s/events" % (self.config['url'], tenant_id)

    def make_request(self, logger, time, tenant_and_metric=None):

        if tenant_and_metric is None:
            tenant_id = self.user.get_tenant_id()
            metric_id = random.randint(
                1, self.config['annotations_per_tenant'])
            tenant_and_metric = [tenant_id, metric_id]
            url = self.ingest_url()
        else:
            tenant_id, metric_id = tenant_and_metric
            url = self.ingest_url(tenant_id)

        payload = self.generate_payload(time, metric_id)

        headers = ( NVPair("Content-Type", "application/json"), )
        result = self.request.POST(url, payload, headers)
        return result
