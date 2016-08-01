import random

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
from abstract_thread import AbstractThread, default_config, generate_job_range
from abstract_thread import generate_metrics_tenants, generate_metric_name


class AnnotationsIngestThread(AbstractThread):
    # The list of metric numbers for all threads in this worker
    annotations = []

    @classmethod
    def create_metrics(cls, agent_number, config=default_config):
        """ Generate all the annotations for this worker

        """
        cls.annotations = generate_metrics_tenants(
            config['annotations_num_tenants'],
            config['annotations_per_tenant'], agent_number,
            config['num_nodes'],
            cls.generate_annotations_for_tenant)

    @classmethod
    def num_threads(cls, config=default_config):
        return config['annotations_concurrency']

    @staticmethod
    def generate_annotations_for_tenant(tenant_id, annotations_per_tenant):
        l = []
        for x in range(annotations_per_tenant):
            l.append([tenant_id, x])
        return l

    def __init__(self, thread_num, agent_num, request, config=None):
        AbstractThread.__init__(self, thread_num, agent_num, config)
        # Initialize the "slice" of the metrics to be sent by this thread
        start, end = generate_job_range(len(self.annotations),
                                        self.num_threads(), thread_num)
        self.slice = self.annotations[start:end]
        self.request = request

    def generate_annotation(self, time, metric_id):
        metric_name = generate_metric_name(metric_id)
        return {'what': 'annotation ' + metric_name,
                'when': time,
                'tags': 'tag',
                'data': 'data'}

    def generate_payload(self, time, metric_id):
        payload = self.generate_annotation(time, metric_id)
        return json.dumps(payload)

    def ingest_url(self, tenant_id):
        return "%s/v2.0/%s/events" % (self.config['url'], tenant_id)

    def make_request(self, logger):
        if len(self.slice) == 0:
            logger("Warning: no work for current thread")
            self.sleep(1000000)
            return None
        self.check_position(logger, len(self.slice))
        batch = self.slice[self.position]
        tenant_id = batch[0]
        metric_id = batch[1]
        payload = self.generate_payload(int(self.time()), metric_id)

        self.position += 1
        result = self.request.POST(self.ingest_url(tenant_id), payload)
        return result
