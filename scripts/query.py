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


class AbstractQueryGenerator(AbstractGenerator):
    one_minute = (1000 * 60)
    one_day = (one_minute * 60 * 24)

    query_interval_name = None

    def __init__(self, thread_num, agent_number, request, config, user=None):
        AbstractGenerator.__init__(self, thread_num, agent_number, request,
                                   config, user)
        self.thread_num = thread_num
        self.config = config
        self.request = request


class SinglePlotQueryGenerator(AbstractQueryGenerator):
    query_interval_name = 'singleplot_query_weight'

    def make_request(self, logger, time, tenant_id=None,
                     metric_name=None):
        if tenant_id is None:
            tenant_id = self.user.get_tenant_id()
        if metric_name is None:
            metric_name = generate_metric_name(
                random.randint(0, self.config['ingest_metrics_per_tenant']),
                self.config)
        to = time
        frm = time - self.one_day
        resolution = 'MIN5'
        url = "%s/v2.0/%s/views/%s?from=%d&to=%s&resolution=%s" % (
            self.config['query_url'],
            tenant_id, metric_name, frm,
            to, resolution)
        result = self.request.GET(url)
        return result


class MultiPlotQueryGenerator(AbstractQueryGenerator):
    query_interval_name = 'multiplot_query_weight'

    def generate_multiplot_payload(self):
        metrics_count = min(self.config['max_multiplot_metrics'],
                            random.randint(0, self.config[
                                'ingest_metrics_per_tenant']))
        metrics_list = [
            generate_metric_name(i, self.config) for i in range(metrics_count)
        ]
        return json.dumps(metrics_list)

    def make_request(self, logger, time, tenant_id=None, payload=None):
        if tenant_id is None:
            tenant_id = self.user.get_tenant_id()
        if payload is None:
            payload = self.generate_multiplot_payload()
        to = time
        frm = time - self.one_day
        resolution = 'MIN5'
        url = "%s/v2.0/%s/views?from=%d&to=%d&resolution=%s" % (
            self.config['query_url'],
            tenant_id, frm,
            to, resolution)
        headers = ( NVPair("Content-Type", "application/json"), )
        result = self.request.POST(url, payload, headers)
        return result


class SearchQueryGenerator(AbstractQueryGenerator):
    query_interval_name = 'search_query_weight'

    def generate_metrics_regex(self):
        metric_name = generate_metric_name(
            random.randint(0, self.config['ingest_metrics_per_tenant']),
            self.config)
        return ".".join(metric_name.split('.')[0:-1]) + ".*"

    def make_request(self, logger, time, tenant_id=None,
                     metric_regex=None):
        if tenant_id is None:
            tenant_id = self.user.get_tenant_id()
        if metric_regex is None:
            metric_regex = self.generate_metrics_regex()
        url = "%s/v2.0/%s/metrics/search?query=%s" % (
            self.config['query_url'],
            tenant_id, metric_regex)
        result = self.request.GET(url)
        return result


class AnnotationsQueryGenerator(AbstractQueryGenerator):
    query_interval_name = 'annotations_query_weight'

    def make_request(self, logger, time, tenant_id=None):
        if tenant_id is None:
            tenant_id = self.user.get_tenant_id()
        to = time
        # Unlike time series data, annotations don't have any kind of rollup, so querying for a day's data can return a
        # huge payload, causing memory issues on the servers when you generate a lot of load.
        frm = time - self.one_minute
        url = "%s/v2.0/%s/events/getEvents?from=%d&until=%d" % (
            self.config['query_url'], tenant_id, frm, to)
        result = self.request.GET(url)
        return result

