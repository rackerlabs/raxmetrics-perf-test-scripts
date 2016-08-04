
from __future__ import division

import sys
import time
import unittest
import random
import math

import ingest
import ingestenum
import query
import annotationsingest
import abstract_thread
import thread_manager as tm

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
import pprint

pp = pprint.pprint
sleep_time = -1
get_url = None
post_url = None
post_payload = None


def mock_sleep(cls, x):
    global sleep_time
    sleep_time = x


class MockReq():
    def __init__(self):
        self.post_url = None
        self.post_payload = None
        self.get_url = None

    def POST(self, url, payload):
        global post_url, post_payload
        post_url = url
        post_payload = payload
        self.post_url = url
        self.post_payload = payload
        return url, payload

    def GET(self, url):
        global get_url
        get_url = url
        self.get_url = url
        return url

requests_by_type = {
    ingest.IngestThread:                        MockReq(),
    ingestenum.EnumIngestThread:                MockReq(),
    annotationsingest.AnnotationsIngestThread:  MockReq(),
    query.QueryThread:                          None,
    query.SinglePlotQuery:                      MockReq(),
    query.MultiPlotQuery:                       MockReq(),
    query.SearchQuery:                          MockReq(),
    query.EnumSearchQuery:                      MockReq(),
    query.EnumSinglePlotQuery:                  MockReq(),
    query.EnumMultiPlotQuery:                   MockReq(),
    query.AnnotationsQuery:                     MockReq(),
}


grinder_props = {
    'grinder.script': '../scripts/tests.py',
    'grinder.package_path': '/Library/Python/2.7/site-packages',
    'grinder.runs': '1',
    'grinder.threads': '45',
    'grinder.useConsole': 'false',
    'grinder.logDirectory': 'resources/logs',
    'grinder.bf.name_fmt': 'org.example.metric.%d',
    'grinder.bf.report_interval': '10000',
    'grinder.bf.annotations_num_tenants': '4',
    'grinder.bf.num_tenants': '4',
    'grinder.bf.enum_num_tenants': '4',
    'grinder.bf.metrics_per_tenant': '15',
    'grinder.bf.enum_metrics_per_tenant': '5',
    'grinder.bf.batch_size': '5',
    'grinder.bf.ingest_concurrency': '15',
    'grinder.bf.enum_ingest_concurrency': '15',
    'grinder.bf.annotations_per_tenant': '5',
    'grinder.bf.annotations_concurrency': '5',
    'grinder.bf.num_nodes': '1',
    'grinder.bf.url': 'http://metrics-ingest.example.org',
    'grinder.bf.query_url': 'http://metrics.example.org',
    'grinder.bf.query_concurrency': '10',
    'grinder.bf.max_multiplot_metrics': '10',
    'grinder.bf.search_queries_per_interval': '10',
    'grinder.bf.enum_search_queries_per_interval': '10',
    'grinder.bf.multiplot_per_interval': '10',
    'grinder.bf.singleplot_per_interval': '10',
    'grinder.bf.enum_single_plot_queries_per_interval': '10',
    'grinder.bf.enum_multiplot_per_interval': '10',
    'grinder.bf.annotations_queries_per_interval': '8',
}


class TestCaseBase(unittest.TestCase):
    def assertIs(self, expr1, expr2, msg=None):
        return self.assertTrue(expr1 is expr2, msg)

    def assertIsInstance(self, obj, cls, msg=None):
        return self.assertTrue(isinstance(obj, cls), msg)


class InitProcessTest(TestCaseBase):
    def setUp(self):
        self.real_shuffle = random.shuffle
        self.real_randint = random.randint
        self.real_time = abstract_thread.AbstractThread.time
        self.real_sleep = abstract_thread.AbstractThread.sleep
        self.tm = tm.ThreadManager(grinder_props, requests_by_type)
        random.shuffle = lambda x: None
        random.randint = lambda x, y: 0
        abstract_thread.AbstractThread.time = lambda x: 1000
        abstract_thread.AbstractThread.sleep = mock_sleep

        self.test_config = {'report_interval': (1000 * 6),
                            'num_tenants': 3,
                            'enum_num_tenants': 4,
                            'annotations_num_tenants': 3,
                            'metrics_per_tenant': 7,
                            'enum_metrics_per_tenant': 2,
                            'annotations_per_tenant': 2,
                            'batch_size': 3,
                            'ingest_concurrency': 2,
                            'enum_ingest_concurrency': 2,
                            'query_concurrency': 20,
                            'annotations_concurrency': 2,
                            'singleplot_per_interval': 11,
                            'multiplot_per_interval': 10,
                            'search_queries_per_interval': 9,
                            'enum_search_queries_per_interval': 9,
                            'enum_single_plot_queries_per_interval': 10,
                            'enum_multiplot_per_interval': 10,
                            'annotations_queries_per_interval': 8,
                            'name_fmt': "org.example.metric.%d",
                            'num_nodes': 2}

        ingest.default_config.update(self.test_config)

        self.num_query_nodes = self.test_config['num_nodes']
        self.single_plot_queries_agent0 = int(math.ceil(
            self.test_config['singleplot_per_interval'] /
            self.num_query_nodes))
        self.multi_plot_queries_agent0 = int(math.ceil(
            self.test_config['multiplot_per_interval'] /
            self.num_query_nodes))
        self.search_queries_agent0 = int(math.ceil(
            self.test_config[
                'search_queries_per_interval'] / self.num_query_nodes))
        self.enum_search_queries_agent0 = int(math.ceil(
            self.test_config[
                'enum_search_queries_per_interval'] / self.num_query_nodes))
        self.enum_single_plot_queries_agent0 = int(math.ceil(
            self.test_config[
                'enum_single_plot_queries_per_interval'] /
            self.num_query_nodes))
        self.enum_multi_plot_queries_agent0 = int(math.ceil(
            self.test_config[
                'enum_multiplot_per_interval'] / self.num_query_nodes))
        self.annotation_queries_agent0 = int(math.ceil(
            self.test_config[
                'annotations_queries_per_interval'] / self.num_query_nodes))

        self.single_plot_queries_agent1 = \
            self.test_config['singleplot_per_interval'] - \
            self.single_plot_queries_agent0
        self.multi_plot_queries_agent1 = \
            self.test_config['multiplot_per_interval'] - \
            self.multi_plot_queries_agent0
        self.search_queries_agent1 = \
            self.test_config['search_queries_per_interval'] - \
            self.search_queries_agent0
        self.enum_search_queries_agent1 = \
            self.test_config['enum_search_queries_per_interval'] - \
            self.enum_search_queries_agent0
        self.enum_single_plot_queries_agent1 = \
            self.test_config['enum_single_plot_queries_per_interval'] - \
            self.enum_single_plot_queries_agent0
        self.annotation_queries_agent1 = \
            self.test_config['annotations_queries_per_interval'] - \
            self.annotation_queries_agent0
        self.enum_multi_plot_queries_agent1 = \
            self.test_config['enum_multiplot_per_interval'] - \
            self.enum_multi_plot_queries_agent0

    def test_setup_thread_zero(self):
        # confirm that threadnum 0 is an ingest thread
        t1 = self.tm.setup_thread(0, 0)
        self.assertEqual(type(t1), ingest.IngestThread)

    def test_setup_thread_second_type(self):
        # confirm that the threadnum after all ingest threads is
        # EnumIngestThread
        t1 = self.tm.setup_thread(
            self.test_config['enum_ingest_concurrency'], 0)
        self.assertEqual(type(t1), ingestenum.EnumIngestThread)

    def test_setup_thread_third_type(self):
        # confirm that the threadnum after all ingest threads is a query thread
        t1 = self.tm.setup_thread(self.test_config['ingest_concurrency'] +
                                  self.test_config[
                                      'enum_ingest_concurrency'],
                                  0)
        self.assertEqual(type(t1), query.QueryThread)

    def test_setup_thread_fourth_type(self):
        # confirm that the threadnum after all ingest+query threads is an
        # annotations query thread
        t1 = self.tm.setup_thread(self.test_config['ingest_concurrency'] +
                                  self.test_config[
                                      'enum_ingest_concurrency'] +
                                  self.test_config['query_concurrency'],
                                  0)
        self.assertEqual(type(t1), annotationsingest.AnnotationsIngestThread)

    def test_setup_thread_invalid_thread_type(self):
        # confirm that a threadnum after all valid thread types raises an
        # exception
        tot_threads = (
            self.test_config['ingest_concurrency'] +
            self.test_config['enum_ingest_concurrency'] +
            self.test_config['query_concurrency'] +
            self.test_config['annotations_concurrency'])
        self.assertRaises(Exception, self.tm.setup_thread, (tot_threads, 0))

    def test_init_process_annotationsingest_agent_zero(self):

        # confirm that the correct batches of ingest metrics are created for
        # worker 0
        agent_num = 0
        # confirm annotationsingest
        annotationsingest.AnnotationsIngestThread.create_metrics(agent_num)

        self.assertEqual(annotationsingest.AnnotationsIngestThread.annotations,
                         [[0, 0], [0, 1], [1, 0], [1, 1]])

        thread = annotationsingest.AnnotationsIngestThread(
            0, agent_num, MockReq())
        self.assertEqual(thread.slice, [[0, 0], [0, 1]])

        thread = annotationsingest.AnnotationsIngestThread(
            1, agent_num, MockReq())
        self.assertEqual(thread.slice, [[1, 0], [1, 1]])

    def test_init_process_enumingest_agent_zero(self):
        agent_num = 0
        # confirm enum metrics ingest
        ingestenum.EnumIngestThread.create_metrics(agent_num)

        self.assertEqual(ingestenum.EnumIngestThread.metrics,
                         [
                             [[0, 0], [0, 1], [1, 0]],
                             [[1, 1]]
                         ])

        thread = ingestenum.EnumIngestThread(0, agent_num, MockReq())
        self.assertEqual(thread.slice, [[[0, 0], [0, 1], [1, 0]]])

        thread = ingestenum.EnumIngestThread(1, agent_num, MockReq())
        self.assertEqual(thread.slice, [[[1, 1]]])

    def test_init_process_ingest_agent_zero(self):

        agent_num = 0

        # confirm metrics ingest
        ingest.IngestThread.create_metrics(agent_num)

        self.assertEqual(ingest.IngestThread.metrics,
                         [[[0, 0], [0, 1], [0, 2]],
                          [[0, 3], [0, 4], [0, 5]],
                          [[0, 6], [1, 0], [1, 1]],
                          [[1, 2], [1, 3], [1, 4]],
                          [[1, 5], [1, 6]]])

        # confirm that the correct batch slices are created for individual
        # threads
        thread = ingest.IngestThread(0, agent_num, MockReq())
        self.assertEqual(thread.slice,
                         [[[0, 0], [0, 1], [0, 2]],
                          [[0, 3], [0, 4], [0, 5]],
                          [[0, 6], [1, 0], [1, 1]]])
        thread = ingest.IngestThread(1, agent_num, MockReq())
        self.assertEqual(thread.slice,
                         [[[1, 2], [1, 3], [1, 4]],
                          [[1, 5], [1, 6]]])

    def test_init_process_query_agent_zero_create_all_metrics(self):
        agent_num = 0
        # confirm that the number of queries is correctly distributed across
        #  each thread in this worker process
        queries = query.QueryThread._create_metrics(
            agent_num, query.QueryThread.query_types)

        self.assertEqual(
            queries,
            ([query.SinglePlotQuery] * self.single_plot_queries_agent0 +
             [query.MultiPlotQuery] * self.multi_plot_queries_agent0 +
             [query.SearchQuery] * self.search_queries_agent0 +
             [query.EnumSearchQuery] * self.enum_search_queries_agent0 +
             [query.EnumSinglePlotQuery] *
                self.enum_single_plot_queries_agent0 +
             [query.AnnotationsQuery] * self.annotation_queries_agent0) +
            [query.EnumMultiPlotQuery] * self.enum_multi_plot_queries_agent0)

    def test_init_process_query_agent_zero(self):
        agent_num = 0
        # confirm that the number of queries is correctly distributed across
        #  each thread in this worker process

        thread = query.QueryThread(0, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.SinglePlotQuery)
        self.assertIsInstance(thread.slice[1], query.SinglePlotQuery)

        thread = query.QueryThread(3, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.MultiPlotQuery)
        self.assertIsInstance(thread.slice[1], query.MultiPlotQuery)

        thread = query.QueryThread(6, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.SearchQuery)
        self.assertIsInstance(thread.slice[1], query.SearchQuery)

        thread = query.QueryThread(9, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.EnumSearchQuery)
        self.assertIsInstance(thread.slice[1], query.EnumSearchQuery)

        thread = query.QueryThread(12, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.EnumSinglePlotQuery)
        self.assertIsInstance(thread.slice[1], query.EnumSinglePlotQuery)

        thread = query.QueryThread(14, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.AnnotationsQuery)
        self.assertIsInstance(thread.slice[1], query.AnnotationsQuery)

        thread = query.QueryThread(16, agent_num, requests_by_type)
        self.assertEqual(1, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.EnumMultiPlotQuery)

    def test_init_process_ingest_agent_one(self):

        agent_num = 1

        # confirm that the correct batches of ingest metrics are created for
        # worker 1
        ingest.IngestThread.create_metrics(agent_num)

        self.assertEqual(ingest.IngestThread.metrics,
                         [[[2, 0], [2, 1], [2, 2]],
                          [[2, 3], [2, 4], [2, 5]],
                          [[2, 6]]])

        thread = ingest.IngestThread(0, agent_num, MockReq())
        self.assertEqual(thread.slice,
                         [[[2, 0], [2, 1], [2, 2]],
                          [[2, 3], [2, 4], [2, 5]]])
        thread = ingest.IngestThread(1, agent_num, MockReq())
        self.assertEqual(thread.slice,
                         [[[2, 6]]])

    def test_init_process_annotationsingest_agent_one(self):
        agent_num = 1
        annotationsingest.AnnotationsIngestThread.create_metrics(agent_num)
        self.assertEqual(annotationsingest.AnnotationsIngestThread.annotations,
                         [[2, 0], [2, 1]])

    def test_init_process_query_agent_one_create_all_metrics(self):
        agent_num = 1
        queries = query.QueryThread._create_metrics(
            agent_num, query.QueryThread.query_types)

        # confirm that the correct batches of queries are created for worker 1

        self.assertEqual(
            queries,
            ([query.SinglePlotQuery] * self.single_plot_queries_agent1 +
             [query.MultiPlotQuery] * self.multi_plot_queries_agent1 +
             [query.SearchQuery] * self.search_queries_agent1 +
             [query.EnumSearchQuery] * self.enum_search_queries_agent1 +
             [query.EnumSinglePlotQuery] *
                self.enum_single_plot_queries_agent1 +
             [query.AnnotationsQuery] * self.annotation_queries_agent1) +
            [query.EnumMultiPlotQuery] * self.enum_multi_plot_queries_agent1)

    def test_init_process_query_agent_one(self):
        agent_num = 1

        thread = query.QueryThread(0, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.SinglePlotQuery)
        self.assertIsInstance(thread.slice[1], query.SinglePlotQuery)

        thread = query.QueryThread(4, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.MultiPlotQuery)
        self.assertIsInstance(thread.slice[1], query.MultiPlotQuery)

        thread = query.QueryThread(6, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.SearchQuery)
        self.assertIsInstance(thread.slice[1], query.SearchQuery)

        thread = query.QueryThread(8, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.EnumSearchQuery)
        self.assertIsInstance(thread.slice[1], query.EnumSearchQuery)

        thread = query.QueryThread(10, agent_num, requests_by_type)
        self.assertEqual(2, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.EnumSinglePlotQuery)
        self.assertIsInstance(thread.slice[1], query.EnumSinglePlotQuery)

        thread = query.QueryThread(12, agent_num, requests_by_type)
        self.assertEqual(1, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.AnnotationsQuery)

        thread = query.QueryThread(16, agent_num, requests_by_type)
        self.assertEqual(1, len(thread.slice))
        self.assertIsInstance(thread.slice[0], query.EnumMultiPlotQuery)

    def tearDown(self):
        random.shuffle = self.real_shuffle
        random.randint = self.real_randint
        abstract_thread.AbstractThread.time = self.real_time
        abstract_thread.AbstractThread.sleep = self.real_sleep


class GeneratePayloadTest(TestCaseBase):
    def setUp(self):
        self.real_shuffle = random.shuffle
        self.real_randint = random.randint
        self.real_time = abstract_thread.AbstractThread.time
        self.real_sleep = abstract_thread.AbstractThread.sleep
        random.shuffle = lambda x: None
        random.randint = lambda x, y: 0
        abstract_thread.AbstractThread.time = lambda x: 1000
        abstract_thread.AbstractThread.sleep = mock_sleep

        self.test_config = {'report_interval': (1000 * 6),
                            'num_tenants': 3,
                            'enum_num_tenants': 4,
                            'annotations_num_tenants': 3,
                            'metrics_per_tenant': 7,
                            'enum_metrics_per_tenant': 2,
                            'annotations_per_tenant': 2,
                            'batch_size': 3,
                            'ingest_concurrency': 2,
                            'enum_ingest_concurrency': 2,
                            'query_concurrency': 20,
                            'annotations_concurrency': 2,
                            'singleplot_per_interval': 11,
                            'multiplot_per_interval': 10,
                            'search_queries_per_interval': 9,
                            'enum_search_queries_per_interval': 9,
                            'enum_single_plot_queries_per_interval': 10,
                            'enum_multiplot_per_interval': 10,
                            'annotations_queries_per_interval': 8,
                            'name_fmt': "org.example.metric.%d",
                            'num_nodes': 2}

        ingest.default_config.update(self.test_config)

    def test_generate_payload(self):
        agent_num = 1
        ingest.IngestThread.create_metrics(agent_num)
        thread = ingest.IngestThread(0, agent_num, MockReq())
        payload = json.loads(
            thread.generate_payload(0, [[2, 3], [2, 4], [2, 5]]))
        valid_payload = [{u'collectionTime': 0,
                          u'metricName': u'org.example.metric.3',
                          u'metricValue': 0,
                          u'tenantId': u'2',
                          u'ttlInSeconds': 172800,
                          u'unit': u'days'},
                         {u'collectionTime': 0,
                          u'metricName': u'org.example.metric.4',
                          u'metricValue': 0,
                          u'tenantId': u'2',
                          u'ttlInSeconds': 172800,
                          u'unit': u'days'},
                         {u'collectionTime': 0,
                          u'metricName': u'org.example.metric.5',
                          u'metricValue': 0,
                          u'tenantId': u'2',
                          u'ttlInSeconds': 172800,
                          u'unit': u'days'}]
        self.assertEqual(payload, valid_payload)

    def test_generate_enum_payload(self):
        agent_num = 1
        ingestenum.EnumIngestThread.create_metrics(agent_num)
        thread = ingestenum.EnumIngestThread(0, agent_num, MockReq())
        payload = json.loads(thread.generate_payload(1, [[2, 1], [2, 2]]))
        valid_payload = [{
            u'timestamp': 1,
            u'tenantId': u'2',
            u'enums': [{
                u'value': u'e_g_1_0',
                u'name': ingestenum.EnumIngestThread.
                         generate_enum_metric_name(1)
            }]},
            {
                u'timestamp': 1,
                u'tenantId': u'2',
                u'enums': [{
                    u'value': u'e_g_2_0',
                    u'name': ingestenum.EnumIngestThread.
                             generate_enum_metric_name(2)
                }]
            }
        ]
        self.assertEqual(payload, valid_payload)

    def test_generate_annotations_payload(self):
        agent_num = 1
        annotationsingest.AnnotationsIngestThread.create_metrics(agent_num)
        thread = annotationsingest.AnnotationsIngestThread(
            0, agent_num, MockReq())
        payload = json.loads(thread.generate_payload(0, 3))
        valid_payload = {
            'what': 'annotation org.example.metric.3',
            'when': 0,
            'tags': 'tag',
            'data': 'data'}
        self.assertEqual(payload, valid_payload)

    def tearDown(self):
        random.shuffle = self.real_shuffle
        random.randint = self.real_randint
        abstract_thread.AbstractThread.time = self.real_time
        abstract_thread.AbstractThread.sleep = self.real_sleep


class MakeAnnotationsIngestRequestsTest(TestCaseBase):
    def setUp(self):
        self.real_shuffle = random.shuffle
        self.real_randint = random.randint
        self.real_time = abstract_thread.AbstractThread.time
        self.real_sleep = abstract_thread.AbstractThread.sleep
        random.shuffle = lambda x: None
        random.randint = lambda x, y: 0
        abstract_thread.AbstractThread.time = lambda x: 1000
        abstract_thread.AbstractThread.sleep = mock_sleep

        self.test_config = {'report_interval': (1000 * 6),
                            'num_tenants': 3,
                            'enum_num_tenants': 4,
                            'annotations_num_tenants': 3,
                            'metrics_per_tenant': 7,
                            'enum_metrics_per_tenant': 2,
                            'annotations_per_tenant': 2,
                            'batch_size': 3,
                            'ingest_concurrency': 2,
                            'enum_ingest_concurrency': 2,
                            'query_concurrency': 20,
                            'annotations_concurrency': 2,
                            'singleplot_per_interval': 11,
                            'multiplot_per_interval': 10,
                            'search_queries_per_interval': 9,
                            'enum_search_queries_per_interval': 9,
                            'enum_single_plot_queries_per_interval': 10,
                            'enum_multiplot_per_interval': 10,
                            'annotations_queries_per_interval': 8,
                            'name_fmt': "org.example.metric.%d",
                            'num_nodes': 2}

        ingest.default_config.update(self.test_config)

    def test_annotationsingest_make_request(self):
        global sleep_time
        agent_num = 0
        thread = annotationsingest.AnnotationsIngestThread(
            0, agent_num, MockReq())
        thread.slice = [[2, 0]]
        thread.position = 0
        thread.finish_time = 10000
        valid_payload = {
            "what": "annotation org.example.metric.0",
            "when": 1000, "tags": "tag", "data": "data"}

        url, payload = thread.make_request(pp)
        # confirm request generates proper URL and payload
        self.assertEqual(
            url,
            'http://metrics-ingest.example.org/v2.0/2/events')
        self.assertEqual(eval(payload), valid_payload)

        # confirm request increments position if not at end of report interval
        self.assertEqual(thread.position, 1)
        self.assertEqual(thread.finish_time, 10000)
        thread.position = 2
        thread.make_request(pp)

        # confirm request resets position at end of report interval
        self.assertEqual(sleep_time, 9000)
        self.assertEqual(thread.position, 1)
        self.assertEqual(thread.finish_time, 16000)

    def tearDown(self):
        random.shuffle = self.real_shuffle
        random.randint = self.real_randint
        abstract_thread.AbstractThread.time = self.real_time
        abstract_thread.AbstractThread.sleep = self.real_sleep


class MakeIngestRequestsTest(TestCaseBase):
    def setUp(self):
        self.real_shuffle = random.shuffle
        self.real_randint = random.randint
        self.real_time = abstract_thread.AbstractThread.time
        self.real_sleep = abstract_thread.AbstractThread.sleep
        random.shuffle = lambda x: None
        random.randint = lambda x, y: 0
        abstract_thread.AbstractThread.time = lambda x: 1000
        abstract_thread.AbstractThread.sleep = mock_sleep

        self.test_config = {'report_interval': (1000 * 6),
                            'num_tenants': 3,
                            'enum_num_tenants': 4,
                            'annotations_num_tenants': 3,
                            'metrics_per_tenant': 7,
                            'enum_metrics_per_tenant': 2,
                            'annotations_per_tenant': 2,
                            'batch_size': 3,
                            'ingest_concurrency': 2,
                            'enum_ingest_concurrency': 2,
                            'query_concurrency': 20,
                            'annotations_concurrency': 2,
                            'singleplot_per_interval': 11,
                            'multiplot_per_interval': 10,
                            'search_queries_per_interval': 9,
                            'enum_search_queries_per_interval': 9,
                            'enum_single_plot_queries_per_interval': 10,
                            'enum_multiplot_per_interval': 10,
                            'annotations_queries_per_interval': 8,
                            'name_fmt': "org.example.metric.%d",
                            'num_nodes': 2}

        ingest.default_config.update(self.test_config)

    def test_ingest_make_request(self):
        global sleep_time
        agent_num = 0
        thread = ingest.IngestThread(0, agent_num, MockReq())
        thread.slice = [[[2, 0], [2, 1]]]
        thread.position = 0
        thread.finish_time = 10000
        valid_payload = [
            {"collectionTime": 1000, "ttlInSeconds": 172800, "tenantId": "2",
             "metricValue": 0, "unit": "days",
             "metricName": "org.example.metric.0"},
            {"collectionTime": 1000, "ttlInSeconds": 172800, "tenantId": "2",
             "metricValue": 0, "unit": "days",
             "metricName": "org.example.metric.1"}]

        url, payload = thread.make_request(pp)
        # confirm request generates proper URL and payload
        self.assertEqual(
            url,
            'http://metrics-ingest.example.org/v2.0/tenantId/ingest/multi')
        self.assertEqual(eval(payload), valid_payload)

        # confirm request increments position if not at end of report interval
        self.assertEqual(thread.position, 1)
        self.assertEqual(thread.finish_time, 10000)
        thread.position = 2
        thread.make_request(pp)
        # confirm request resets position at end of report interval
        self.assertEqual(sleep_time, 9000)
        self.assertEqual(thread.position, 1)
        self.assertEqual(thread.finish_time, 16000)

    def tearDown(self):
        random.shuffle = self.real_shuffle
        random.randint = self.real_randint
        abstract_thread.AbstractThread.time = self.real_time
        abstract_thread.AbstractThread.sleep = self.real_sleep


class MakeIngestEnumRequestsTest(TestCaseBase):
    def setUp(self):
        self.real_shuffle = random.shuffle
        self.real_randint = random.randint
        self.real_time = abstract_thread.AbstractThread.time
        self.real_sleep = abstract_thread.AbstractThread.sleep
        random.shuffle = lambda x: None
        random.randint = lambda x, y: 0
        abstract_thread.AbstractThread.time = lambda x: 1000
        abstract_thread.AbstractThread.sleep = mock_sleep

        self.test_config = {'report_interval': (1000 * 6),
                            'num_tenants': 3,
                            'enum_num_tenants': 4,
                            'annotations_num_tenants': 3,
                            'metrics_per_tenant': 7,
                            'enum_metrics_per_tenant': 2,
                            'annotations_per_tenant': 2,
                            'batch_size': 3,
                            'ingest_concurrency': 2,
                            'enum_ingest_concurrency': 2,
                            'query_concurrency': 20,
                            'annotations_concurrency': 2,
                            'singleplot_per_interval': 11,
                            'multiplot_per_interval': 10,
                            'search_queries_per_interval': 9,
                            'enum_search_queries_per_interval': 9,
                            'enum_single_plot_queries_per_interval': 10,
                            'enum_multiplot_per_interval': 10,
                            'annotations_queries_per_interval': 8,
                            'name_fmt': "org.example.metric.%d",
                            'num_nodes': 2}

        ingest.default_config.update(self.test_config)

    def test_ingest_enum_make_request(self):
        global sleep_time
        agent_num = 0
        thread = ingestenum.EnumIngestThread(0, agent_num, MockReq())
        thread.slice = [[[2, 0], [2, 1]]]
        thread.position = 0
        thread.finish_time = 10000
        valid_payload = [
            {
                'tenantId': '2',
                'timestamp': 1000,
                'enums': [{
                    'value': 'e_g_0_0',
                    'name': ingestenum.EnumIngestThread.
                            generate_enum_metric_name(0)
                }]
            },
            {
                'tenantId': '2',
                'timestamp': 1000,
                'enums': [{
                    'value': 'e_g_1_0',
                    'name': ingestenum.EnumIngestThread.
                            generate_enum_metric_name(1)
                }]
            }
        ]

        url, payload = thread.make_request(pp)
        # confirm request generates proper URL and payload
        self.assertEqual(url,
                         'http://metrics-ingest.example.org/v2.0/tenantId/' +
                         'ingest/aggregated/multi')
        self.assertEqual(eval(payload), valid_payload)

        # confirm request increments position if not at end of report interval
        self.assertEqual(thread.position, 1)
        self.assertEqual(thread.finish_time, 10000)
        thread.position = 2
        thread.make_request(pp)
        # confirm request resets position at end of report interval
        self.assertEqual(sleep_time, 9000)
        self.assertEqual(thread.position, 1)
        self.assertEqual(thread.finish_time, 16000)

    def tearDown(self):
        random.shuffle = self.real_shuffle
        random.randint = self.real_randint
        abstract_thread.AbstractThread.time = self.real_time
        abstract_thread.AbstractThread.sleep = self.real_sleep


class MakeQueryRequestsTest(TestCaseBase):
    def setUp(self):
        self.agent_num = 0
        self.num_threads = query.QueryThread.num_threads()
        self.requests_by_type = requests_by_type.copy()
        self.thread = query.QueryThread(0, self.agent_num, self.requests_by_type)
        self.config = abstract_thread.default_config.copy()

    def test_make_request_calls_make_request(self):
        generate_was_called = []
        expected_result = object()

        class DummyQueryType(query.AbstractQuery):
            def make_request(self, time, logger, request, *args, **kwargs):
                generate_was_called.append(True)
                return expected_result
            query_interval_name = 'DummyQueryType_per_interval'
        self.config['DummyQueryType_per_interval'] = 3
        self.requests_by_type[DummyQueryType] = MockReq()
        random.randint = lambda x, y: 40
        req = requests_by_type[query.SinglePlotQuery]
        qq = DummyQueryType(0, self.agent_num, self.num_threads, self.config)
        self.thread.slice = [qq]
        self.thread.position = 0

        # pre-condition
        self.assertEquals(0, self.thread.position)

        # when
        result = self.thread.make_request(pp)

        # then
        self.assertEquals([True], generate_was_called)
        self.assertIs(expected_result, result)
        self.assertEquals(1, self.thread.position)

    def test_query_make_SinglePlotQuery_request(self):
        random.randint = lambda x, y: 40
        req = requests_by_type[query.SinglePlotQuery]
        qq = query.SinglePlotQuery(0, self.agent_num, self.num_threads, self.config)
        result = qq.make_request(1000, None, req, 0,
                             'org.example.metric.metric123')
        self.assertEqual(req.get_url,
                         "http://metrics.example.org/v2.0/0/views/" +
                         "org.example.metric.metric123?from=-86399000&" +
                         "to=1000&resolution=FULL")
        self.assertEquals(req.get_url, result)

    def test_query_make_SearchQuery_request(self):
        req = requests_by_type[query.SearchQuery]
        qq = query.SearchQuery(0, self.agent_num, self.num_threads, self.config)
        result = qq.make_request(1000, None, req, 10,
                             'org.example.metric.*')
        self.assertEqual(req.get_url,
                         "http://metrics.example.org/v2.0/10/metrics/search?" +
                         "query=org.example.metric.*")
        self.assertEquals(req.get_url, result)

    def test_query_make_MultiPlotQuery_request(self):
        req = requests_by_type[query.MultiPlotQuery]
        qq = query.MultiPlotQuery(0, self.agent_num, self.num_threads, self.config)
        payload_sent = json.dumps([
            "org.example.metric.0",
            "org.example.metric.1",
            "org.example.metric.2",
            "org.example.metric.3",
            "org.example.metric.4",
            "org.example.metric.5",
            "org.example.metric.6",
            "org.example.metric.7",
            "org.example.metric.8",
            "org.example.metric.9"
        ])
        result = qq.make_request(1000, None, req, 20,
                                 payload_sent)
        self.assertEqual(req.post_url,
                         "http://metrics.example.org/v2.0/20/views?" +
                         "from=-86399000&to=1000&resolution=FULL")
        self.assertEqual(req.post_payload, payload_sent)
        self.assertEquals((req.post_url, req.post_payload), result)

    def test_query_make_AnnotationsQuery_request(self):
        req = requests_by_type[query.AnnotationsQuery]
        qq = query.AnnotationsQuery(0, self.agent_num, self.num_threads, self.config)
        result = qq.make_request(1000, None, req, 30)
        self.assertEqual(req.get_url,
                         "http://metrics.example.org/v2.0/30/events/" +
                         "getEvents?from=-86399000&until=1000")
        self.assertEquals(req.get_url, result)

    def test_query_make_EnumSearchQuery_request(self):
        req = requests_by_type[query.EnumSearchQuery]
        qq = query.EnumSearchQuery(0, self.agent_num, self.num_threads, self.config)
        result = qq.make_request(1000, None, req, 40)
        self.assertEqual(req.get_url,
                         "http://metrics.example.org/v2.0/40/metrics/search?" +
                         "query=enum_grinder_org.example.metric.*&" +
                         "include_enum_values=true")
        self.assertEquals(req.get_url, result)

    def test_query_make_EnumSinglePlotQuery_request(self):
        req = requests_by_type[query.EnumSinglePlotQuery]
        qq = query.EnumSinglePlotQuery(0, self.agent_num, self.num_threads, self.config)
        result = qq.make_request(1000, None, req, 50,
                             'enum_grinder_org.example.metric.metric456')
        self.assertEqual(req.get_url,
                         "http://metrics.example.org/v2.0/50/views/" +
                         "enum_grinder_org.example.metric.metric456?" +
                         "from=-86399000&to=1000&resolution=FULL")
        self.assertEquals(req.get_url, result)

    def test_query_make_EnumMultiPlotQuery_request(self):
        req = requests_by_type[query.EnumMultiPlotQuery]
        qq = query.EnumMultiPlotQuery(0, self.agent_num, self.num_threads, self.config)
        payload_sent = json.dumps([
            "enum_grinder_org.example.metric.0",
            "enum_grinder_org.example.metric.1",
            "enum_grinder_org.example.metric.2",
            "enum_grinder_org.example.metric.3"
        ])
        result = qq.make_request(1000, None, req, 4,
                                 payload_sent)
        self.assertEqual(req.post_url,
                         "http://metrics.example.org/v2.0/4/views?" +
                         "from=-86399000&to=1000&resolution=FULL")
        self.assertEqual(req.post_payload, payload_sent)
        self.assertEquals((req.post_url, req.post_payload), result)


suite = unittest.TestSuite()
loader = unittest.TestLoader()
suite.addTest(loader.loadTestsFromTestCase(InitProcessTest))
suite.addTest(loader.loadTestsFromTestCase(GeneratePayloadTest))
suite.addTest(loader.loadTestsFromTestCase(MakeAnnotationsIngestRequestsTest))
suite.addTest(loader.loadTestsFromTestCase(MakeIngestRequestsTest))
suite.addTest(loader.loadTestsFromTestCase(MakeIngestEnumRequestsTest))
suite.addTest(loader.loadTestsFromTestCase(MakeQueryRequestsTest))
unittest.TextTestRunner().run(suite)


class TestRunner:
    def __init__(self):
        pass

    def __call__(self):
        pass
