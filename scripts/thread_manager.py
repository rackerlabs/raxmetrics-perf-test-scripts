#!/usr/bin/env python

import ast

from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest

from abstract_thread import default_config
from annotationsingest import AnnotationsIngestThread
from ingest import IngestThread
from ingestenum import EnumIngestThread
from query import QueryThread, SinglePlotQuery, MultiPlotQuery, SearchQuery
from query import EnumSearchQuery, EnumSinglePlotQuery, AnnotationsQuery
from query import EnumMultiPlotQuery

__grinder_tests_by_request_object = {}


def create_request_obj(test_num, test_name):
    test = Test(test_num, test_name)
    request = HTTPRequest()
    __grinder_tests_by_request_object[request] = test
    test.record(request)
    return request


class ThreadManager(object):
    # keep track of the various thread types
    thread_types = []

    def __init__(self, config, thread_types=None):
        if thread_types is None:
            thread_types = [IngestThread, EnumIngestThread, QueryThread,
                            AnnotationsIngestThread]
        # tot_threads is the value passed to the grinder at startup for the
        # number of threads to start
        self.tot_threads = 0

        # concurrent_threads is the sum of the various thread types, (currently
        # ingest and query)
        self.concurrent_threads = 0
        self.setup_config(config)

        # Sanity check the concurrent_threads to make sure they are the same as
        # the value
        #  passed to the grinder
        if self.tot_threads != self.concurrent_threads:
            raise Exception(
                "Configuration error: grinder.threads doesn't equal total "
                "concurrent threads")

        self.thread_types = thread_types

        self.ingest_request = create_request_obj(1, "Ingest test")
        self.enum_ingest_request = create_request_obj(7, "Enum Ingest test")
        self.annotations_ingest_request = create_request_obj(
            2, "Annotations Ingest test")
        self.query_single_plot_request = create_request_obj(
            3, "SinglePlotQuery")
        self.query_multi_plot_request = create_request_obj(4, "MultiPlotQuery")
        self.query_search_request = create_request_obj(5, "SearchQuery")
        self.query_annotations_request = create_request_obj(
            6, "AnnotationsQuery")
        self.query_enum_search_request = create_request_obj(
            8, "EnumSearchQuery")
        self.query_enum_single_plot_request = create_request_obj(
            9, "EnumSinglePlotQuery")
        self.query_enum_multi_plot_request = create_request_obj(
            10, "EnumMultiPlotQuery")

        self.requests_by_query_type = {
                SinglePlotQuery:        self.query_single_plot_request,
                MultiPlotQuery:         self.query_multi_plot_request,
                SearchQuery:            self.query_search_request,
                EnumSearchQuery:        self.query_enum_search_request,
                EnumSinglePlotQuery:    self.query_enum_single_plot_request,
                EnumMultiPlotQuery:     self.query_enum_multi_plot_request,
                AnnotationsQuery:       self.query_annotations_request,
            }

    def get_grinder_request_object_by_thread_type(self, thread_type):
        if thread_type is IngestThread:
            return self.ingest_request
        if thread_type is EnumIngestThread:
            return self.enum_ingest_request
        if thread_type is AnnotationsIngestThread:
            return self.annotations_ingest_request
        if thread_type is QueryThread:
            return self.requests_by_query_type  # note that this is a dictionary
        raise TypeError("Unknown thread type: %s" % str(thread_type))

    def setup_config(self, config):
        # Parse the properties file and update default_config dictionary
        for k, v in config.iteritems():
            if v.startswith(".."):
                continue
            if k == "grinder.threads":
                self.tot_threads = self.convert(v)
            if k.find("concurrency") >= 0:
                self.concurrent_threads += self.convert(v)
            if not k.startswith("grinder.bf."):
                continue
            k = k.replace("grinder.bf.", "")
            default_config[k] = self.convert(v)

    def convert(self, s):
        try:
            return int(s)
        except:
            pass
        if isinstance(s, basestring):
            if s[0] in ("'", '"'):
                return ast.literal_eval(s)
            return s
        return str(s)

    def create_all_metrics(self, agent_number):
        """Step through all the attached types and have them create their
        metrics"""
        for x in self.thread_types:
            x.create_metrics(agent_number)

    def setup_thread(self, thread_num):
        """Figure out which type thread to create based on thread_num and
        return it

        Creates threads of various types for use by the grinder to load
        test various parts of blueflood.  The code is structured so that
        the thread type is determined by the thread num.  The grinder
        properties file determines how many of each type to create based
        on the "ingest_concurrency" and "query_concurrency" options.

        So for example, if "ingest_concurrency" is set to 4, and
        "query_concurrency" is set to 2, thread numbers 0-3 will be ingest
        threads and thread numbers 4-5 will be query threads.

        """
        thread_type = None
        server_num = thread_num

        for x in self.thread_types:
            if server_num < x.num_threads():
                thread_type = x
                break
            else:
                server_num -= x.num_threads()

        if thread_type is None:
            raise Exception("Invalid Thread Type")

        req = self.get_grinder_request_object_by_thread_type(thread_type)

        return thread_type(server_num, req)
