import random

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
from abstract_thread import AbstractThread
from throttling_group import NullThrottlingGroup

try:
    from HTTPClient import NVPair
except ImportError:
    from nvpair import NVPair


class EnumIngestThread(AbstractThread):

    # TODO: Add enum prefix to config
    @staticmethod
    def generate_enum_metric_name(metric_id, config):
        return "enum_grinder_" + config['name_fmt'] % metric_id

    def generate_enum_suffix(self):
        return "_" + str(random.randint(0, self.config['enum_num_values']))

    def generate_enum_metric(self, time, tenant_id, metric_id, value):
        return {'tenantId': str(tenant_id),
                'timestamp': time,
                'enums': [{'name': self.generate_enum_metric_name(metric_id,
                                                                  self.config),
                           'value': value}]
                }

    def generate_payload(self, time, tenant_metric_id_values):
        payload = [self.generate_enum_metric(time, tmv[0], tmv[1], tmv[2])
                   for tmv in tenant_metric_id_values]
        return json.dumps(payload)

    def ingest_url(self):
        return "%s/v2.0/tenantId/ingest/aggregated/multi" % self.config[
            'url']

    def make_request(self, logger, time, tenant_metric_id_values=None):
        if tenant_metric_id_values is None:
            tenant_metric_id_values = []
            for i in xrange(self.config['enum_batch_size']):
                tenant_id = random.randint(1, self.config['enum_num_tenants'])
                metric_id = random.randint(
                    1, self.config['enum_metrics_per_tenant'])
                value = 'e_g_' + str(metric_id) + self.generate_enum_suffix()
                tmv = [tenant_id, metric_id, value]
                tenant_metric_id_values.append(tmv)
        payload = self.generate_payload(time, tenant_metric_id_values)
        headers = ( NVPair("Content-Type", "application/json"), )
        result = self.request.POST(self.ingest_url(), payload, headers)
        if result.getStatusCode() >= 400:
            logger("Error: status code=" + str(result.getStatusCode()) + " response=" + result.getText())
        return result
