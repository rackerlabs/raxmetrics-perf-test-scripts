
try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
from abstract_thread import AbstractThread, generate_job_range
from abstract_thread import generate_metric_name, shuffled


class AnnotationsIngestThread(AbstractThread):
    # The list of metric numbers for all threads in this worker
    annotations = []

    @staticmethod
    def _create_metrics(agent_number, config):
        """ Generate all the annotations for this worker

        """
        num_tenants = config['annotations_num_tenants']
        metrics_per_tenant = config['annotations_per_tenant']
        num_nodes = config['num_nodes']

        """generate the subset of the total metrics to be done by this agent"""
        tenants_in_shard = range(
            *generate_job_range(num_tenants, num_nodes, agent_number))
        metrics = []
        for y in [AnnotationsIngestThread.generate_annotations_for_tenant(x, metrics_per_tenant) for x in
                     tenants_in_shard]:
            metrics += y
        return shuffled(metrics)

    @classmethod
    def num_threads(cls, config):
        return config['annotations_weight']

    @staticmethod
    def generate_annotations_for_tenant(tenant_id, annotations_per_tenant):
        l = []
        for x in range(annotations_per_tenant):
            l.append([tenant_id, x])
        return l

    def __init__(self, thread_num, agent_num, request, config):
        AbstractThread.__init__(self, thread_num, agent_num, request, config)
        self.annotations = self._create_metrics(self.agent_num, self.config)
        # Initialize the "slice" of the metrics to be sent by this thread
        start, end = generate_job_range(len(self.annotations),
                                        self.num_threads(self.config),
                                        thread_num)
        self.slice = self.annotations[start:end]

    def generate_annotation(self, time, metric_id):
        metric_name = generate_metric_name(metric_id, self.config)
        return {'what': 'annotation ' + metric_name,
                'when': time,
                'tags': 'tag',
                'data': 'data'}

    def generate_payload(self, time, metric_id):
        payload = self.generate_annotation(time, metric_id)
        return json.dumps(payload)

    def ingest_url(self, tenant_id):
        return "%s/v2.0/%s/events" % (self.config['url'], tenant_id)

    def make_request(self, logger, time):
        if len(self.slice) == 0:
            logger("Warning: no work for current thread")
            return None
        self.check_position(logger, len(self.slice))
        batch = self.get_next_item()
        tenant_id = batch[0]
        metric_id = batch[1]
        payload = self.generate_payload(int(self.time()), metric_id)

        result = self.request.POST(self.ingest_url(tenant_id), payload)
        return result
