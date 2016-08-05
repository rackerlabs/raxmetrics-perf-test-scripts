import random

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
from abstract_thread import AbstractThread, generate_job_range
from abstract_thread import generate_metric_name
from ingestenum import EnumIngestThread


class AbstractQuery(AbstractThread):
    one_day = (1000 * 60 * 60 * 24)

    query_interval_name = None

    @classmethod
    def num_threads(cls, config):
        return config[cls.query_interval_name]

    @staticmethod
    def _get_num_queries_for_current_node(agent_number, query_interval_name,
                                          config):
        total_queries = config[query_interval_name]
        start_job, end_job = generate_job_range(
            total_queries, config['num_nodes'], agent_number)
        num_queries_for_current_node = end_job - start_job

        return num_queries_for_current_node

    @classmethod
    def get_num_queries_for_current_node(cls, agent_number,
                                         config):
        return cls._get_num_queries_for_current_node(agent_number,
                                                     cls.query_interval_name,
                                                     config)

    @staticmethod
    def _create_metrics(cls, agent_number, query_interval_name,
                        config):
        # divide the total number of each query type into the ones need by this
        # worker
        num = AbstractQuery._get_num_queries_for_current_node(
            agent_number, query_interval_name, config)

        return [cls] * num

    @classmethod
    def create_metrics(cls, agent_number, config):
        # divide the total number of each query type into the ones need by this
        # worker
        queries = cls._create_metrics(
            cls, agent_number, cls.query_interval_name, config)
        return queries

    def __init__(self, thread_num, agent_number, request, config):
        AbstractThread.__init__(self, thread_num, agent_number, request, config)
        self.thread_num = thread_num
        self.config = config
        self.queries = self._create_metrics(
            self, agent_number, self.query_interval_name, config)
        self.request = request

    def make_request(self, logger, time):
        return self._make_request(logger, time)

    def _make_request(self, logger, time, tenant_id=None):
        raise Exception("Can't instantiate abstract query")


class SinglePlotQuery(AbstractQuery):
    query_interval_name = 'singleplot_per_interval'

    def _make_request(self, logger, time, tenant_id=None,
                      metric_name=None):
        if tenant_id is None:
            tenant_id = random.randint(0, self.config['num_tenants'])
        if metric_name is None:
            metric_name = generate_metric_name(
                random.randint(0, self.config['metrics_per_tenant']),
                self.config)
        to = time
        frm = time - self.one_day
        resolution = 'FULL'
        url = "%s/v2.0/%d/views/%s?from=%d&to=%s&resolution=%s" % (
            self.config['query_url'],
            tenant_id, metric_name, frm,
            to, resolution)
        result = self.request.GET(url)
        #    logger(result.getText())
        return result


class MultiPlotQuery(AbstractQuery):
    query_interval_name = 'multiplot_per_interval'

    def generate_multiplot_payload(self):
        metrics_count = min(self.config['max_multiplot_metrics'],
                            random.randint(0, self.config[
                                'metrics_per_tenant']))
        metrics_list = [
            generate_metric_name(i, self.config) for i in range(metrics_count)
        ]
        return json.dumps(metrics_list)

    def _make_request(self, logger, time, tenant_id=None, payload=None):
        if tenant_id is None:
            tenant_id = random.randint(0, self.config['num_tenants'])
        if payload is None:
            payload = self.generate_multiplot_payload()
        to = time
        frm = time - self.one_day
        resolution = 'FULL'
        url = "%s/v2.0/%d/views?from=%d&to=%d&resolution=%s" % (
            self.config['query_url'],
            tenant_id, frm,
            to, resolution)
        result = self.request.POST(url, payload)
        #    logger(result.getText())
        return result


class SearchQuery(AbstractQuery):
    query_interval_name = 'search_queries_per_interval'

    def generate_metrics_regex(self):
        metric_name = generate_metric_name(
            random.randint(0, self.config['metrics_per_tenant']), self.config)
        return ".".join(metric_name.split('.')[0:-1]) + ".*"

    def _make_request(self, logger, time, tenant_id=None,
                      metric_regex=None):
        if tenant_id is None:
            tenant_id = random.randint(0, self.config['num_tenants'])
        if metric_regex is None:
            metric_regex = self.generate_metrics_regex()
        url = "%s/v2.0/%d/metrics/search?query=%s" % (
            self.config['query_url'],
            tenant_id, metric_regex)
        result = self.request.GET(url)
        #    logger(result.getText())
        return result


class AnnotationsQuery(AbstractQuery):
    query_interval_name = 'annotations_queries_per_interval'

    def _make_request(self, logger, time, tenant_id=None):
        if tenant_id is None:
            tenant_id = random.randint(0,
                                       self.config['annotations_num_tenants'])
        to = time
        frm = time - self.one_day
        url = "%s/v2.0/%d/events/getEvents?from=%d&until=%d" % (
            self.config['query_url'], tenant_id, frm, to)
        result = self.request.GET(url)
        return result


class EnumSearchQuery(AbstractQuery):
    query_interval_name = 'enum_search_queries_per_interval'

    def generate_metrics_regex(self):
        metric_name = 'enum_grinder_' + generate_metric_name(
            random.randint(0, self.config['enum_metrics_per_tenant']),
            self.config)
        return ".".join(metric_name.split('.')[0:-1]) + ".*"

    def _make_request(self, logger, time, tenant_id=None,
                      metric_regex=None):
        if tenant_id is None:
            tenant_id = random.randint(0, self.config['enum_num_tenants'])
        if metric_regex is None:
            metric_regex = self.generate_metrics_regex()
        url = "%s/v2.0/%d/metrics/search?query=%s&include_enum_values=true" % (
            self.config['query_url'],
            tenant_id, metric_regex)
        result = self.request.GET(url)
        return result


class EnumSinglePlotQuery(AbstractQuery):
    query_interval_name = 'enum_single_plot_queries_per_interval'

    def _make_request(self, logger, time, tenant_id=None,
                      metric_name=None):
        if tenant_id is None:
            tenant_id = random.randint(0, self.config['enum_num_tenants'])
        if metric_name is None:
            metric_name = EnumIngestThread.generate_enum_metric_name(
                random.randint(0, self.config['enum_metrics_per_tenant']),
                self.config)
        to = time
        frm = time - self.one_day
        resolution = 'FULL'
        url = "%s/v2.0/%d/views/%s?from=%d&to=%s&resolution=%s" % (
            self.config['query_url'],
            tenant_id, metric_name, frm,
            to, resolution)
        result = self.request.GET(url)
        #    logger(result.getText())
        return result


class EnumMultiPlotQuery(AbstractQuery):
    query_interval_name = 'enum_multiplot_per_interval'

    def generate_multiplot_payload(self):
        metrics_count = min(self.config['max_multiplot_metrics'],
                            random.randint(0, self.config[
                                'enum_metrics_per_tenant']))
        metrics_list = [
            EnumIngestThread.generate_enum_metric_name(i, self.config) for i in
            range(metrics_count)]
        return json.dumps(metrics_list)

    def _make_request(self, logger, time, tenant_id=None, payload=None):
        if tenant_id is None:
            tenant_id = random.randint(0, self.config['enum_num_tenants'])
        if payload is None:
            payload = self.generate_multiplot_payload()
        to = time
        frm = time - self.one_day
        resolution = 'FULL'
        url = "%s/v2.0/%d/views?from=%d&to=%d&resolution=%s" % (
            self.config['query_url'],
            tenant_id, frm,
            to, resolution)
        result = self.request.POST(url, payload)
        #    logger(result.getText())
        return result
