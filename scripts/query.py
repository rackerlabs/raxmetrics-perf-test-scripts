import random

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
import itertools
from abstract_thread import AbstractThread, default_config, generate_job_range
from abstract_thread import generate_metric_name, generate_enum_metric_name


class AbstractQuery(object):
    one_day = (1000 * 60 * 60 * 24)

    query_interval_name = None
    num_queries_for_current_node = 0

    @classmethod
    def create_metrics(cls, agent_number, config=default_config):
        # divide the total number of each query type into the ones need by this
        # worker
        total_queries = config[cls.query_interval_name]
        start_job, end_job = generate_job_range(
            total_queries, config['num_nodes'], agent_number)
        cls.num_queries_for_current_node = end_job - start_job

        return [cls] * cls.num_queries_for_current_node

    def __init__(self, thread_num, num_threads, config):
        self.thread_num = thread_num
        self.num_threads = num_threads
        self.config = config

    def generate(self, time, logger, request):
        raise Exception("Can't instantiate abstract query")


class SinglePlotQuery(AbstractQuery):
    query_interval_name = 'singleplot_per_interval'

    def generate(self, time, logger, request):
        tenant_id = random.randint(0, self.config['num_tenants'])
        metric_name = generate_metric_name(
            random.randint(0, self.config['metrics_per_tenant']))
        to = time
        frm = time - self.one_day
        resolution = 'FULL'
        url = "%s/v2.0/%d/views/%s?from=%d&to=%s&resolution=%s" % (
            self.config['query_url'],
            tenant_id, metric_name, frm,
            to, resolution)
        result = request.GET(url)
        #    logger(result.getText())
        return result


class MultiPlotQuery(AbstractQuery):
    query_interval_name = 'multiplot_per_interval'

    def generate_multiplot_payload(self):
        metrics_count = min(self.config['max_multiplot_metrics'],
                            random.randint(0, self.config[
                                'metrics_per_tenant']))
        metrics_list = map(generate_metric_name,
                           range(metrics_count))
        return json.dumps(metrics_list)

    def generate(self, time, logger, request):
        tenant_id = random.randint(0, self.config['num_tenants'])
        payload = self.generate_multiplot_payload()
        to = time
        frm = time - self.one_day
        resolution = 'FULL'
        url = "%s/v2.0/%d/views?from=%d&to=%d&resolution=%s" % (
            self.config['query_url'],
            tenant_id, frm,
            to, resolution)
        result = request.POST(url, payload)
        #    logger(result.getText())
        return result


class SearchQuery(AbstractQuery):
    query_interval_name = 'search_queries_per_interval'

    def generate_metrics_regex(self):
        metric_name = generate_metric_name(
            random.randint(0, self.config['metrics_per_tenant']))
        return ".".join(metric_name.split('.')[0:-1]) + ".*"

    def generate(self, time, logger, request):
        tenant_id = random.randint(0, self.config['num_tenants'])
        metric_regex = self.generate_metrics_regex()
        url = "%s/v2.0/%d/metrics/search?query=%s" % (
            self.config['query_url'],
            tenant_id, metric_regex)
        result = request.GET(url)
        #    logger(result.getText())
        return result


class AnnotationsQuery(AbstractQuery):
    query_interval_name = 'annotations_queries_per_interval'

    def generate(self, time, logger, request):
        tenant_id = random.randint(0,
                                   self.config['annotations_num_tenants'])
        to = time
        frm = time - self.one_day
        url = "%s/v2.0/%d/events/getEvents?from=%d&until=%d" % (
            self.config['query_url'], tenant_id, frm, to)
        result = request.GET(url)
        return result


class EnumSearchQuery(AbstractQuery):
    query_interval_name = 'enum_search_queries_per_interval'

    def generate_metrics_regex(self):
        metric_name = 'enum_grinder_' + generate_metric_name(
            random.randint(0, self.config['enum_metrics_per_tenant']))
        return ".".join(metric_name.split('.')[0:-1]) + ".*"

    def generate(self, time, logger, request):
        tenant_id = random.randint(0, self.config['enum_num_tenants'])
        metric_regex = self.generate_metrics_regex()
        url = "%s/v2.0/%d/metrics/search?query=%s&include_enum_values=true" % (
            self.config['query_url'],
            tenant_id, metric_regex)
        result = request.GET(url)
        return result


class EnumSinglePlotQuery(AbstractQuery):
    query_interval_name = 'enum_single_plot_queries_per_interval'

    def generate(self, time, logger, request):
        tenant_id = random.randint(0, self.config['enum_num_tenants'])
        metric_name = generate_enum_metric_name(
            random.randint(0, self.config['enum_metrics_per_tenant']))
        to = time
        frm = time - self.one_day
        resolution = 'FULL'
        url = "%s/v2.0/%d/views/%s?from=%d&to=%s&resolution=%s" % (
            self.config['query_url'],
            tenant_id, metric_name, frm,
            to, resolution)
        result = request.GET(url)
        #    logger(result.getText())
        return result


class EnumMultiPlotQuery(AbstractQuery):
    query_interval_name = 'enum_multiplot_per_interval'

    def generate_multiplot_payload(self):
        metrics_count = min(self.config['max_multiplot_metrics'],
                            random.randint(0, self.config[
                                'enum_metrics_per_tenant']))
        metrics_list = map(generate_enum_metric_name,
                           range(metrics_count))
        return json.dumps(metrics_list)

    def generate(self, time, logger, request):
        tenant_id = random.randint(0, self.config['enum_num_tenants'])
        payload = self.generate_multiplot_payload()
        to = time
        frm = time - self.one_day
        resolution = 'FULL'
        url = "%s/v2.0/%d/views?from=%d&to=%d&resolution=%s" % (
            self.config['query_url'],
            tenant_id, frm,
            to, resolution)
        result = request.POST(url, payload)
        #    logger(result.getText())
        return result


class QueryThread(AbstractThread):
    # The list of queries to be invoked across all threads in this worker
    queries = []

    query_types = [SinglePlotQuery, MultiPlotQuery, SearchQuery,
                   EnumSearchQuery, EnumSinglePlotQuery, AnnotationsQuery,
                   EnumMultiPlotQuery]

    @staticmethod
    def _create_metrics(agent_number, query_types):
        queries = list(itertools.chain(
            *[x.create_metrics(agent_number) for x in query_types]))
        random.shuffle(queries)
        return queries

    @classmethod
    def create_metrics(cls, agent_number, query_types):
        cls.queries = cls._create_metrics(agent_number, query_types)

    @classmethod
    def num_threads(cls, config=default_config):
        return config['query_concurrency']

    def __init__(self, thread_num, agent_num, requests_by_query_type, config=None):
        AbstractThread.__init__(self, thread_num, agent_num, config)
        self.query_instances = [
            x(thread_num, self.num_threads(), self.config) for x in
            self.query_types]
        self.requests_by_query_type = requests_by_query_type
        total_queries_for_current_node = reduce(
            lambda x, y: x + y,
            [x.num_queries_for_current_node
             for x in self.query_instances])
        start, end = generate_job_range(total_queries_for_current_node,
                                        self.num_threads(),
                                        thread_num)

        self.queries = self._create_metrics(self.agent_num, self.query_types)
        self.slice = self.queries[start:end]
        self.query_fn_dict = dict(
            [[type(x), x.generate] for x in self.query_instances])

    def make_request(self, logger):
        if len(self.slice) == 0:
            logger("Warning: no work for current thread")
            self.sleep(1000000)
            return None
        self.check_position(logger, len(self.slice))
        query_type = self.slice[self.position]
        request = self.requests_by_query_type[query_type]
        result = self.query_fn_dict[query_type](
            int(self.time()), logger, request)
        self.position += 1
        return result
