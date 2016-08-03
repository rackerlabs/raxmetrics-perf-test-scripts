import random

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
import itertools
from abstract_thread import AbstractThread, default_config, generate_job_range
from abstract_thread import generate_metric_name, generate_enum_metric_name
from abstract_thread import shuffled


class AbstractQuery(object):
    one_day = (1000 * 60 * 60 * 24)

    query_interval_name = None

    @staticmethod
    def _get_num_queries_for_current_node(agent_number, query_interval_name,
                                          config=default_config):
        total_queries = config[query_interval_name]
        start_job, end_job = generate_job_range(
            total_queries, config['num_nodes'], agent_number)
        num_queries_for_current_node = end_job - start_job

        return num_queries_for_current_node

    @classmethod
    def get_num_queries_for_current_node(cls, agent_number,
                                         config=default_config):
        return cls._get_num_queries_for_current_node(agent_number,
                                                     cls.query_interval_name,
                                                     config)

    @staticmethod
    def _create_metrics(cls, agent_number, query_interval_name,
                        config=default_config):
        # divide the total number of each query type into the ones need by this
        # worker
        num = AbstractQuery._get_num_queries_for_current_node(
            agent_number, query_interval_name, config)

        return [cls] * num

    @classmethod
    def create_metrics(cls, agent_number, config=default_config):
        # divide the total number of each query type into the ones need by this
        # worker
        queries = cls._create_metrics(
            cls, agent_number, cls.query_interval_name, config)
        return queries

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

    query_types = [SinglePlotQuery, MultiPlotQuery, SearchQuery,
                   EnumSearchQuery, EnumSinglePlotQuery, AnnotationsQuery,
                   EnumMultiPlotQuery]

    @staticmethod
    def _create_metrics(agent_number, query_types):
        queries = []
        for qtype in query_types:
            qq = qtype._create_metrics(qtype, agent_number,
                                       qtype.query_interval_name)
            queries.extend(qq)
        return queries

    @classmethod
    def num_threads(cls, config=default_config):
        return config['query_concurrency']

    def __init__(self, thread_num, agent_num, requests_by_query_type, config=None):
        AbstractThread.__init__(self, thread_num, agent_num, config)
        self.query_instances = [
            SinglePlotQuery(thread_num, self.num_threads(), self.config),
            MultiPlotQuery(thread_num, self.num_threads(), self.config),
            SearchQuery(thread_num, self.num_threads(), self.config),
            EnumSearchQuery(thread_num, self.num_threads(), self.config),
            EnumSinglePlotQuery(thread_num, self.num_threads(), self.config),
            AnnotationsQuery(thread_num, self.num_threads(), self.config),
            EnumMultiPlotQuery(thread_num, self.num_threads(), self.config)
        ]
        self.query_instances_by_type = {
            SinglePlotQuery:        self.query_instances[0],
            MultiPlotQuery:         self.query_instances[1],
            SearchQuery:            self.query_instances[2],
            EnumSearchQuery:        self.query_instances[3],
            EnumSinglePlotQuery:    self.query_instances[4],
            AnnotationsQuery:       self.query_instances[5],
            EnumMultiPlotQuery:     self.query_instances[6],
        }
        queries = shuffled(
            self._create_metrics(self.agent_num, self.query_instances))
        self.requests_by_query_type = requests_by_query_type
        total_queries_for_current_node = 0
        for qi in self.query_instances:
            total_queries_for_current_node += \
                qi.get_num_queries_for_current_node(agent_num)
        start, end = generate_job_range(total_queries_for_current_node,
                                        self.num_threads(),
                                        thread_num)

        self.slice = queries[start:end]

    def make_request(self, logger):
        if len(self.slice) == 0:
            logger("Warning: no work for current thread")
            self.sleep(1000000)
            return None
        self.check_position(logger, len(self.slice))
        query_instance_or_type = self.slice[self.position]
        if issubclass(query_instance_or_type, AbstractQuery):
            query = self.query_instances_by_type[query_instance_or_type]
        else:
            query = query_instance_or_type
        request = self.requests_by_query_type[type(query)]
        result = query.generate(
            int(self.time()), logger, request)
        self.position += 1
        return result
