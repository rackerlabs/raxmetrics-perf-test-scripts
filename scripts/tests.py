
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
from config import clean_configs
from throttling_group import ThrottlingGroup
from throttling_request import ThrottlingRequest
from authenticating_request import AuthenticatingRequest
from user import User

try:
    from com.xhaus.jyson import JysonCodec as json
except ImportError:
    import json
import pprint

try:
    from HTTPClient import NVPair
except ImportError:
    from nvpair import NVPair

pp = pprint.pprint
sleep_time = -1
get_url = None
post_url = None
post_payload = None


def mock_sleep(cls, x):
    global sleep_time
    sleep_time = x


class MockResponse(object):
    def __init__(self, request, status_code=200):
        self.request = request
        self.status_code = status_code

    def getStatusCode(self):
        return self.status_code


class MockReq(object):
    def __init__(self):
        self.post_url = None
        self.post_payload = None
        self.get_url = None
        self.headers = None

    def POST(self, url, payload, headers=None):
        global post_url, post_payload
        post_url = url
        post_payload = payload
        self.post_url = url
        self.post_payload = payload
        self.headers = headers
        return MockResponse(self)

    def GET(self, url, payload=None, headers=None):
        global get_url
        get_url = url
        self.get_url = url
        self.headers = headers
        return MockResponse(self)

requests_by_type = {
    ingest.IngestThread:                        MockReq(),
    ingestenum.EnumIngestThread:                MockReq(),
    annotationsingest.AnnotationsIngestThread:  MockReq(),
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

    'grinder.bf.url': 'http://metrics-ingest.example.org',
    'grinder.bf.query_url': 'http://metrics.example.org',

    'grinder.bf.name_fmt': 'org.example.metric.%d',
    'grinder.bf.max_multiplot_metrics': '10',

    'grinder.bf.ingest_weight': '15',
    'grinder.bf.num_tenants': '4',
    'grinder.bf.metrics_per_tenant': '15',
    'grinder.bf.ingest_batch_size': '5',

    'grinder.bf.enum_ingest_weight': '0',
    'grinder.bf.enum_num_tenants': '4',
    'grinder.bf.enum_metrics_per_tenant': '5',
    'grinder.bf.enum_batch_size': '5',

    'grinder.bf.annotations_weight': '5',
    'grinder.bf.annotations_num_tenants': '4',
    'grinder.bf.annotations_per_tenant': '5',

    'grinder.bf.singleplot_query_weight': '2',

    'grinder.bf.multiplot_query_weight': '2',

    'grinder.bf.search_query_weight': '2',

    'grinder.bf.enum_search_query_weight': '0',

    'grinder.bf.enum_single_plot_query_weight': '0',

    'grinder.bf.enum_multiplot_query_weight': '0',

    'grinder.bf.annotations_query_weight': '1',
}


class TestCaseBase(unittest.TestCase):
    def assertIs(self, expr1, expr2, msg=None):
        return self.assertTrue(expr1 is expr2, msg)

    def assertIsInstance(self, obj, cls, msg=None):
        return self.assertTrue(isinstance(obj, cls), msg)
    pass


class ThreadManagerTest(TestCaseBase):
    def setUp(self):
        config = grinder_props.copy()
        config.update({
            'grinder.bf.enum_ingest_weight': 15,
            'grinder.bf.enum_search_query_weight': 1,
            'grinder.bf.enum_single_plot_query_weight': 1,
            'grinder.bf.enum_multiplot_query_weight': 1,
        })
        self.tm = tm.ThreadManager(config, requests_by_type)

        self.test_config = abstract_thread.default_config.copy()
        self.test_config.update(clean_configs(grinder_props))

    def test_thread_type_assignment_0(self):
        th = self.tm.setup_thread(0, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_1(self):
        th = self.tm.setup_thread(1, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_2(self):
        th = self.tm.setup_thread(2, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_3(self):
        th = self.tm.setup_thread(3, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_4(self):
        th = self.tm.setup_thread(4, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_5(self):
        th = self.tm.setup_thread(5, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_6(self):
        th = self.tm.setup_thread(6, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_7(self):
        th = self.tm.setup_thread(7, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_8(self):
        th = self.tm.setup_thread(8, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_9(self):
        th = self.tm.setup_thread(9, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_10(self):
        th = self.tm.setup_thread(10, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_11(self):
        th = self.tm.setup_thread(11, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_12(self):
        th = self.tm.setup_thread(12, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_13(self):
        th = self.tm.setup_thread(13, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_14(self):
        th = self.tm.setup_thread(14, 0)
        self.assertEqual(type(th), ingest.IngestThread)

    def test_thread_type_assignment_15(self):
        th = self.tm.setup_thread(15, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_16(self):
        th = self.tm.setup_thread(16, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_17(self):
        th = self.tm.setup_thread(17, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_18(self):
        th = self.tm.setup_thread(18, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_19(self):
        th = self.tm.setup_thread(19, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_20(self):
        th = self.tm.setup_thread(20, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_21(self):
        th = self.tm.setup_thread(21, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_22(self):
        th = self.tm.setup_thread(22, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_23(self):
        th = self.tm.setup_thread(23, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_24(self):
        th = self.tm.setup_thread(24, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_25(self):
        th = self.tm.setup_thread(25, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_26(self):
        th = self.tm.setup_thread(26, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_27(self):
        th = self.tm.setup_thread(27, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_28(self):
        th = self.tm.setup_thread(28, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_29(self):
        th = self.tm.setup_thread(29, 0)
        self.assertEqual(type(th), ingestenum.EnumIngestThread)

    def test_thread_type_assignment_30(self):
        th = self.tm.setup_thread(30, 0)
        self.assertEqual(type(th), annotationsingest.AnnotationsIngestThread)

    def test_thread_type_assignment_31(self):
        th = self.tm.setup_thread(31, 0)
        self.assertEqual(type(th), annotationsingest.AnnotationsIngestThread)

    def test_thread_type_assignment_32(self):
        th = self.tm.setup_thread(32, 0)
        self.assertEqual(type(th), annotationsingest.AnnotationsIngestThread)

    def test_thread_type_assignment_33(self):
        th = self.tm.setup_thread(33, 0)
        self.assertEqual(type(th), annotationsingest.AnnotationsIngestThread)

    def test_thread_type_assignment_34(self):
        th = self.tm.setup_thread(34, 0)
        self.assertEqual(type(th), annotationsingest.AnnotationsIngestThread)

    def test_thread_type_assignment_35(self):
        th = self.tm.setup_thread(35, 0)
        self.assertEqual(type(th), query.SinglePlotQuery)

    def test_thread_type_assignment_36(self):
        th = self.tm.setup_thread(36, 0)
        self.assertEqual(type(th), query.SinglePlotQuery)

    def test_thread_type_assignment_37(self):
        th = self.tm.setup_thread(37, 0)
        self.assertEqual(type(th), query.MultiPlotQuery)

    def test_thread_type_assignment_38(self):
        th = self.tm.setup_thread(38, 0)
        self.assertEqual(type(th), query.MultiPlotQuery)

    def test_thread_type_assignment_39(self):
        th = self.tm.setup_thread(39, 0)
        self.assertEqual(type(th), query.SearchQuery)

    def test_thread_type_assignment_40(self):
        th = self.tm.setup_thread(40, 0)
        self.assertEqual(type(th), query.SearchQuery)

    def test_thread_type_assignment_41(self):
        th = self.tm.setup_thread(41, 0)
        self.assertEqual(type(th), query.EnumSearchQuery)

    def test_thread_type_assignment_42(self):
        th = self.tm.setup_thread(42, 0)
        self.assertEqual(type(th), query.EnumSinglePlotQuery)

    def test_thread_type_assignment_43(self):
        th = self.tm.setup_thread(43, 0)
        self.assertEqual(type(th), query.EnumMultiPlotQuery)

    def test_thread_type_assignment_44(self):
        th = self.tm.setup_thread(44, 0)
        self.assertEqual(type(th), query.AnnotationsQuery)

    def test_setup_thread_invalid_thread_type(self):
        self.assertRaises(Exception, self.tm.setup_thread, (45, 0))


class InitProcessTest(TestCaseBase):
    def setUp(self):
        self.test_config = abstract_thread.default_config.copy()
        self.test_config.update(clean_configs(grinder_props))
        self.test_config.update({
            'name_fmt': "org.example.metric.%d",

            'ingest_weight': 2,
            'ingest_num_tenants': 3,
            'ingest_metrics_per_tenant': 7,
            'ingest_batch_size': 3,

            'enum_ingest_weight': 0,
            'enum_num_tenants': 4,
            'enum_metrics_per_tenant': 2,
            'enum_batch_size': 3,

            'annotations_weight': 2,
            'annotations_num_tenants': 3,
            'annotations_per_tenant': 2,

            'singleplot_query_weight': 11,

            'multiplot_query_weight': 10,

            'search_query_weight': 9,

            'enum_search_query_weight': 0,

            'enum_single_plot_query_weight': 0,

            'enum_multiplot_query_weight': 0,

            'annotations_query_weight': 8,
        })


class GeneratePayloadTest(TestCaseBase):
    def setUp(self):
        self.test_config = abstract_thread.default_config.copy()
        self.test_config.update({
            'name_fmt': "org.example.metric.%d",

            'ingest_weight': 2,
            'ingest_num_tenants': 3,
            'ingest_metrics_per_tenant': 7,
            'ingest_batch_size': 3,

            'enum_ingest_weight': 0,
            'enum_num_tenants': 4,
            'enum_metrics_per_tenant': 2,
            'enum_batch_size': 3,

            'annotations_weight': 2,
            'annotations_num_tenants': 3,
            'annotations_per_tenant': 2,

            'singleplot_query_weight': 11,

            'multiplot_query_weight': 10,

            'search_query_weight': 9,

            'enum_search_query_weight': 0,

            'enum_single_plot_query_weight': 0,

            'enum_multiplot_query_weight': 0,

            'annotations_query_weight': 8,
        })

    def test_generate_payload(self):
        agent_num = 1
        thread = ingest.IngestThread(0, agent_num, MockReq(), self.test_config)
        payload = json.loads(
            thread.generate_payload(0, [[2, 3, 0], [2, 4, 0], [2, 5, 0]]))
        valid_payload = [{'collectionTime': 0,
                          'metricName': 'org.example.metric.3',
                          'metricValue': 0,
                          'tenantId': '2',
                          'ttlInSeconds': 172800,
                          'unit': 'days'},
                         {'collectionTime': 0,
                          'metricName': 'org.example.metric.4',
                          'metricValue': 0,
                          'tenantId': '2',
                          'ttlInSeconds': 172800,
                          'unit': 'days'},
                         {'collectionTime': 0,
                          'metricName': 'org.example.metric.5',
                          'metricValue': 0,
                          'tenantId': '2',
                          'ttlInSeconds': 172800,
                          'unit': 'days'}]
        self.assertEqual(payload, valid_payload)

    def test_generate_enum_payload(self):
        agent_num = 1
        thread = ingestenum.EnumIngestThread(0, agent_num, MockReq(),
                                             self.test_config)
        payload = json.loads(
            thread.generate_payload(1, [[2, 1, 'e_g_1_0'], [2, 2, 'e_g_2_0']]))
        valid_payload = [{
            'timestamp': 1,
            'tenantId': '2',
            'enums': [{
                'value': 'e_g_1_0',
                'name': ingestenum.EnumIngestThread.
                         generate_enum_metric_name(1, self.test_config)
            }]},
            {
                'timestamp': 1,
                'tenantId': '2',
                'enums': [{
                    'value': 'e_g_2_0',
                    'name': ingestenum.EnumIngestThread.
                             generate_enum_metric_name(2, self.test_config)
                }]
            }
        ]
        self.assertEqual(payload, valid_payload)

    def test_generate_annotations_payload(self):
        agent_num = 1
        thread = annotationsingest.AnnotationsIngestThread(
            0, agent_num, MockReq(), self.test_config)
        payload = json.loads(thread.generate_payload(0, 3))
        valid_payload = {
            'what': 'annotation org.example.metric.3',
            'when': 0,
            'tags': 'tag',
            'data': 'data'}
        self.assertEqual(payload, valid_payload)


class MakeAnnotationsIngestRequestsTest(TestCaseBase):
    def setUp(self):
        self.test_config = abstract_thread.default_config.copy()
        self.test_config.update({
            'url': 'http://metrics-ingest.example.org',
            'query_url': 'http://metrics.example.org',

            'name_fmt': "org.example.metric.%d",

            'ingest_weight': 2,
            'ingest_num_tenants': 3,
            'ingest_metrics_per_tenant': 7,
            'ingest_batch_size': 3,

            'enum_ingest_weight': 0,
            'enum_num_tenants': 4,
            'enum_metrics_per_tenant': 2,
            'enum_batch_size': 3,

            'annotations_weight': 2,
            'annotations_num_tenants': 3,
            'annotations_per_tenant': 2,

            'singleplot_query_weight': 11,

            'multiplot_query_weight': 10,

            'search_query_weight': 9,

            'enum_search_query_weight': 0,

            'enum_single_plot_query_weight': 0,

            'enum_multiplot_query_weight': 0,

            'annotations_query_weight': 8,
        })

    def test_annotationsingest_make_request(self):
        global sleep_time
        agent_num = 0
        thread = annotationsingest.AnnotationsIngestThread(
            0, agent_num, MockReq(), self.test_config)
        tenant_id = 2
        metric_id = 4
        valid_payload = {
            "what": "annotation org.example.metric.%s" % metric_id,
            "when": 1000, "tags": "tag", "data": "data"}

        response = thread.make_request(pp, 1000, tenant_id, metric_id)
        url = response.request.post_url
        payload = response.request.post_payload

        # confirm request generates proper URL and payload
        self.assertEqual(
            url,
            'http://metrics-ingest.example.org/v2.0/2/events')
        self.assertEqual(eval(payload), valid_payload)


class MakeIngestRequestsTest(TestCaseBase):
    def setUp(self):
        self.test_config = abstract_thread.default_config.copy()
        self.test_config.update({
            'url': 'http://metrics-ingest.example.org',
            'query_url': 'http://metrics.example.org',

            'name_fmt': "org.example.metric.%d",

            'ingest_weight': 2,
            'ingest_num_tenants': 3,
            'ingest_metrics_per_tenant': 7,
            'ingest_batch_size': 3,

            'enum_ingest_weight': 0,
            'enum_num_tenants': 4,
            'enum_metrics_per_tenant': 2,
            'enum_batch_size': 3,

            'annotations_weight': 2,
            'annotations_num_tenants': 3,
            'annotations_per_tenant': 2,

            'singleplot_query_weight': 11,

            'multiplot_query_weight': 10,

            'search_query_weight': 9,

            'enum_search_query_weight': 0,

            'enum_single_plot_query_weight': 0,

            'enum_multiplot_query_weight': 0,

            'annotations_query_weight': 8,
        })

    def test_ingest_make_request(self):
        global sleep_time
        agent_num = 0
        thread = ingest.IngestThread(0, agent_num, MockReq(), self.test_config)
        valid_payload = [
            {"collectionTime": 1000, "ttlInSeconds": 172800, "tenantId": "2",
             "metricValue": 0, "unit": "days",
             "metricName": "org.example.metric.0"},
            {"collectionTime": 1000, "ttlInSeconds": 172800, "tenantId": "2",
             "metricValue": 0, "unit": "days",
             "metricName": "org.example.metric.1"}]

        tenant_metric_id_values = [
            [2, 0, 0],
            [2, 1, 0]
        ]
        response = thread.make_request(pp, 1000, tenant_metric_id_values)
        url = response.request.post_url
        payload = response.request.post_payload

        # confirm request generates proper URL and payload
        self.assertEqual(
            url,
            'http://metrics-ingest.example.org/v2.0/tenantId/ingest/multi')
        self.assertEqual(eval(payload), valid_payload)


class MakeIngestEnumRequestsTest(TestCaseBase):
    def setUp(self):
        self.test_config = abstract_thread.default_config.copy()
        self.test_config.update({
            'url': 'http://metrics-ingest.example.org',
            'query_url': 'http://metrics.example.org',

            'name_fmt': "org.example.metric.%d",

            'ingest_weight': 2,
            'ingest_num_tenants': 3,
            'ingest_metrics_per_tenant': 7,
            'ingest_batch_size': 3,

            'enum_ingest_weight': 0,
            'enum_num_tenants': 4,
            'enum_metrics_per_tenant': 2,
            'enum_batch_size': 3,

            'annotations_weight': 2,
            'annotations_num_tenants': 3,
            'annotations_per_tenant': 2,

            'singleplot_query_weight': 11,

            'multiplot_query_weight': 10,

            'search_query_weight': 9,

            'enum_search_query_weight': 0,

            'enum_single_plot_query_weight': 0,

            'enum_multiplot_query_weight': 0,

            'annotations_query_weight': 8,
        })

    def test_ingest_enum_make_request(self):
        global sleep_time
        agent_num = 0
        thread = ingestenum.EnumIngestThread(0, agent_num, MockReq(),
                                             self.test_config)
        valid_payload = [
            {
                'tenantId': '2',
                'timestamp': 1000,
                'enums': [{
                    'value': 'e_g_0_0',
                    'name': ingestenum.EnumIngestThread.
                            generate_enum_metric_name(0, self.test_config)
                }]
            },
            {
                'tenantId': '2',
                'timestamp': 1000,
                'enums': [{
                    'value': 'e_g_1_0',
                    'name': ingestenum.EnumIngestThread.
                            generate_enum_metric_name(1, self.test_config)
                }]
            }
        ]

        response = thread.make_request(
            pp, 1000,
            tenant_metric_id_values=[[2, 0, 'e_g_0_0'], [2, 1, 'e_g_1_0']])
        url = response.request.post_url
        payload = response.request.post_payload

        # confirm request generates proper URL and payload
        self.assertEqual(url,
                         'http://metrics-ingest.example.org/v2.0/tenantId/' +
                         'ingest/aggregated/multi')
        self.assertEqual(eval(payload), valid_payload)


class MakeQueryRequestsTest(TestCaseBase):
    def setUp(self):
        self.agent_num = 0
        self.config = clean_configs(grinder_props)
        self.requests_by_type = requests_by_type.copy()

    def test_query_make_SinglePlotQuery_request(self):
        req = requests_by_type[query.SinglePlotQuery]
        qq = query.SinglePlotQuery(0, self.agent_num, req, self.config)
        response = qq.make_request(None, 1000, 0, 'org.example.metric.metric123')
        self.assertEqual(req.get_url,
                         "http://metrics.example.org/v2.0/0/views/" +
                         "org.example.metric.metric123?from=-86399000&" +
                         "to=1000&resolution=FULL")
        self.assertIs(req, response.request)

    def test_query_make_SearchQuery_request(self):
        req = requests_by_type[query.SearchQuery]
        qq = query.SearchQuery(0, self.agent_num, req, self.config)
        response = qq.make_request(None, 1000, 10, 'org.example.metric.*')
        self.assertEqual(req.get_url,
                         "http://metrics.example.org/v2.0/10/metrics/search?" +
                         "query=org.example.metric.*")
        self.assertIs(req, response.request)

    def test_query_make_MultiPlotQuery_request(self):
        req = requests_by_type[query.MultiPlotQuery]
        qq = query.MultiPlotQuery(0, self.agent_num, req, self.config)
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
        response = qq.make_request(None, 1000, 20, payload_sent)
        self.assertEqual(req.post_url,
                         "http://metrics.example.org/v2.0/20/views?" +
                         "from=-86399000&to=1000&resolution=FULL")
        self.assertEqual(req.post_payload, payload_sent)
        self.assertIs(req, response.request)

    def test_query_make_AnnotationsQuery_request(self):
        req = requests_by_type[query.AnnotationsQuery]
        qq = query.AnnotationsQuery(0, self.agent_num, req, self.config)
        response = qq.make_request(None, 1000, 30)
        self.assertEqual(req.get_url,
                         "http://metrics.example.org/v2.0/30/events/" +
                         "getEvents?from=-86399000&until=1000")
        self.assertIs(req, response.request)

    def test_query_make_EnumSearchQuery_request(self):
        req = requests_by_type[query.EnumSearchQuery]
        qq = query.EnumSearchQuery(0, self.agent_num, req, self.config)
        response = qq.make_request(None, 1000, 40)
        self.assertEqual(req.get_url,
                         "http://metrics.example.org/v2.0/40/metrics/search?" +
                         "query=enum_grinder_org.example.metric.*&" +
                         "include_enum_values=true")
        self.assertIs(req, response.request)

    def test_query_make_EnumSinglePlotQuery_request(self):
        req = requests_by_type[query.EnumSinglePlotQuery]
        qq = query.EnumSinglePlotQuery(0, self.agent_num, req, self.config)
        response = qq.make_request(None, 1000, 50,
                                 'enum_grinder_org.example.metric.metric456')
        self.assertEqual(req.get_url,
                         "http://metrics.example.org/v2.0/50/views/" +
                         "enum_grinder_org.example.metric.metric456?" +
                         "from=-86399000&to=1000&resolution=FULL")
        self.assertIs(req, response.request)

    def test_query_make_EnumMultiPlotQuery_request(self):
        req = requests_by_type[query.EnumMultiPlotQuery]
        qq = query.EnumMultiPlotQuery(0, self.agent_num, req, self.config)
        payload_sent = json.dumps([
            "enum_grinder_org.example.metric.0",
            "enum_grinder_org.example.metric.1",
            "enum_grinder_org.example.metric.2",
            "enum_grinder_org.example.metric.3"
        ])
        response = qq.make_request(None, 1000, 4, payload_sent)
        self.assertEqual(req.post_url,
                         "http://metrics.example.org/v2.0/4/views?" +
                         "from=-86399000&to=1000&resolution=FULL")
        self.assertEqual(req.post_payload, payload_sent)
        self.assertIs(req, response.request)


class ThrottlingGroupTest(unittest.TestCase):
    def test_throttling(self):
        # given
        times = iter(xrange(10)).next
        last_time_returned = [None]

        def time_source():
            # this time source returns an incrementing sequence of numbers
            # starting from zero
            t = times()
            last_time_returned[0] = t
            return t

        sleeps = []

        def sleep_source(arg):
            # this sleep source just logs what arguments were passed to it, and
            # doesn't actually sleep
            sleeps.append(arg)

        tg = ThrottlingGroup('test', 2, time_source=time_source,
                             sleep_source=sleep_source)

        # when we count the first request
        tg.count_request()

        # then it increments the count and doesn't sleep
        self.assertEquals(1, tg.count)
        self.assertEquals([], sleeps)

        # when we count the second request
        tg.count_request()

        # then it increments the count and doesn't sleep
        self.assertEquals(2, tg.count)
        self.assertEquals([], sleeps)

        # when we count a request over the limit
        tg.count_request()

        # then it sleeps and then resets the count to one
        self.assertEquals(1, tg.count)
        self.assertEquals([60 - 2], sleeps)

    def test_count_reset_after_minute_transpires(self):
        # given
        times = iter([0, 61]).next
        last_time_returned = [None]

        def time_source():
            # this time source returns a fixed sequence of numbers
            t = times()
            last_time_returned[0] = t
            return t

        sleeps = []

        def sleep_source(arg):
            # this sleep source just logs what arguments were passed to it, and
            # doesn't actually sleep
            sleeps.append(arg)

        tg = ThrottlingGroup('test', 2, time_source=time_source,
                             sleep_source=sleep_source)

        # when we count the first request
        tg.count_request()

        # then it increments the count and doesn't sleep
        self.assertEquals(1, tg.count)
        self.assertEquals([], sleeps)

        # when we count the second request
        tg.count_request()

        # then it resets the count to one and doesn't sleep
        self.assertEquals(1, tg.count)
        self.assertEquals([], sleeps)


class ThreadsWithThrottlingGroupTest(unittest.TestCase):
    def test_multiple_threads_share_throttling_group(self):
        # given
        self.test_config = abstract_thread.default_config.copy()
        self.test_config.update({
            'url': 'http://metrics-ingest.example.org',
            'query_url': 'http://metrics.example.org',
            'name_fmt': "org.example.metric.%d",
            'ingest_weight': 1,
            'ingest_num_tenants': 1,
            'ingest_metrics_per_tenant': 1,
            'ingest_batch_size': 1,
            'annotations_weight': 1,
            'annotations_num_tenants': 1,
            'annotations_per_tenant': 1,
            'singleplot_query_weight': 1,
            'multiplot_query_weight': 1,
            'search_query_weight': 1,
            'annotations_query_weight': 1,
        })
        times = iter(xrange(10)).next
        last_time_returned = [None]

        def time_source():
            # this time source returns an incrementing sequence of numbers
            # starting from zero
            t = times()
            last_time_returned[0] = t
            return t

        sleeps = []

        def sleep_source(arg):
            # this sleep source just logs what arguments were passed to it, and
            # doesn't actually sleep
            sleeps.append(arg)

        tgroup = ThrottlingGroup('test', 6, time_source, sleep_source)
        treq = ThrottlingRequest(tgroup, MockReq())

        th1 = ingest.IngestThread(0, 0, treq, self.test_config)
        th2 = annotationsingest.AnnotationsIngestThread(
            1, 0, treq, self.test_config)
        th3 = query.SinglePlotQuery(2, 0, treq, self.test_config)
        th4 = query.MultiPlotQuery(3, 0, treq, self.test_config)
        th5 = query.SearchQuery(4, 0, treq, self.test_config)
        th6 = query.AnnotationsQuery(5, 0, treq, self.test_config)

        # when
        th1.make_request(pp, 1000)
        th2.make_request(pp, 1000)
        th3.make_request(pp, 1000)
        th4.make_request(pp, 1000)
        th5.make_request(pp, 1000)
        th6.make_request(pp, 1000)

        # then
        self.assertEquals([], sleeps)

        # when
        th1.make_request(pp, 1000)

        # then
        self.assertEquals([60 - 6], sleeps)


class AuthenticatingRequestTest(unittest.TestCase):
    def test_adds_token_to_headers(self):

        # given
        req = MockReq()
        token = 'this-is-the-token'
        uri = '/path/to/resource'
        body = 'this is the body'
        ap = AuthenticatingRequest(request=req, token=token)

        # when
        ap.GET(uri, body)

        # then
        self.assertEqual(uri, req.get_url)
        self.assertTrue(req.headers is not None)
        self.assertEqual(1, len(req.headers))
        self.assertTrue(req.headers[0] is not None)
        header = req.headers[0]
        self.assertTrue(isinstance(header, NVPair))
        self.assertEqual('X-Auth-Token', header.getName())
        self.assertEqual(token, header.getValue())


class UserTest(unittest.TestCase):

    token = 'this-is-the-token'
    tenant = 'this-is-the-tenant'
    auth_url = 'https://example.com/v2.0/tokens'
    username = 'user123'
    api_key = '0123456789abcdef0123456789abcdef'

    class DummyResponse(object):
        def json(self):
            return {
                'access': {
                    'token': {
                        'id': UserTest.token,
                        'tenant': {
                            'id': UserTest.tenant }}}}

    class DummyConnector(object):
        called = False
        url = None
        json = None
        headers = None
        def post(self, url, json=None, headers=None):
            self.called = True
            self.url = url
            self.json = json
            self.headers = headers
            return UserTest.DummyResponse()

    def test_constructor_sets_fields(self):

        # when
        user = User(self.auth_url, self.username, self.api_key)

        # then
        self.assertEqual(self.auth_url, user.auth_url)
        self.assertEqual(self.username, user.username)
        self.assertEqual(self.api_key, user.api_key)

    def test_constructor_sets_connector(self):

        # given
        conn = object()

        # when
        user = User(self.auth_url, self.username, self.api_key, connector=conn)

        # then
        self.assertIs(conn, user.connector)

    def test_get_data_makes_a_connection(self):
        # given
        conn = self.DummyConnector()
        user = User(self.auth_url, self.username, self.api_key, connector=conn)

        # precondition
        self.assertFalse(conn.called)
        self.assertIs(None, user.token)
        self.assertIs(None, user.tenant_id)

        # when
        result = user._get_data()

        # then the connector was called
        self.assertTrue(conn.called)

    def test_get_data_sets_tenant_and_token(self):
        # given
        conn = self.DummyConnector()
        user = User(self.auth_url, self.username, self.api_key, connector=conn)

        # precondition
        self.assertFalse(conn.called)
        self.assertIs(None, user.token)
        self.assertIs(None, user.tenant_id)

        # when
        result = user._get_data()

        # then
        self.assertEqual(self.tenant, user.tenant_id)
        self.assertEqual(self.token, user.token)

    def test_get_token_gets_token(self):
        # given
        conn = self.DummyConnector()
        user = User(self.auth_url, self.username, self.api_key, connector=conn)

        # when
        result = user.get_token()

        # then the token was returned
        self.assertEqual(self.token, result)

    def test_get_tenant_id_gets_tenant(self):
        # given
        conn = self.DummyConnector()
        user = User(self.auth_url, self.username, self.api_key, connector=conn)

        # when
        result = user.get_tenant_id()

        # then the token was returned
        self.assertEqual(self.tenant, result)


suite = unittest.TestSuite()
loader = unittest.TestLoader()
suite.addTest(loader.loadTestsFromTestCase(ThreadManagerTest))
suite.addTest(loader.loadTestsFromTestCase(InitProcessTest))
suite.addTest(loader.loadTestsFromTestCase(GeneratePayloadTest))
suite.addTest(loader.loadTestsFromTestCase(MakeAnnotationsIngestRequestsTest))
suite.addTest(loader.loadTestsFromTestCase(MakeIngestRequestsTest))
suite.addTest(loader.loadTestsFromTestCase(MakeIngestEnumRequestsTest))
suite.addTest(loader.loadTestsFromTestCase(MakeQueryRequestsTest))
suite.addTest(loader.loadTestsFromTestCase(ThrottlingGroupTest))
suite.addTest(loader.loadTestsFromTestCase(ThreadsWithThrottlingGroupTest))
suite.addTest(loader.loadTestsFromTestCase(AuthenticatingRequestTest))
suite.addTest(loader.loadTestsFromTestCase(UserTest))
unittest.TextTestRunner().run(suite)


class TestRunner:
    def __init__(self):
        pass

    def __call__(self):
        pass
