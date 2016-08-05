#!/usr/bin/env python

import ast

from abstract_thread import default_config
from annotationsingest import AnnotationsIngestThread
from ingest import IngestThread
from ingestenum import EnumIngestThread
from query import QueryThread, SinglePlotQuery, MultiPlotQuery, SearchQuery
from query import EnumSearchQuery, EnumSinglePlotQuery, AnnotationsQuery
from query import EnumMultiPlotQuery


class ThreadManager(object):
    # keep track of the various thread types
    thread_types = []

    def __init__(self, config, requests_by_type):
        # tot_threads is the value passed to the grinder at startup for the
        # number of threads to start
        self.tot_threads = 0

        # concurrent_threads is the sum of the various thread types, (currently
        # ingest and query)
        self.concurrent_threads = 0

        # Parse the properties file and update default_config dictionary
        self.config = default_config.copy()
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
            self.config[k] = self.convert(v)

        # Sanity check the concurrent_threads to make sure they are the same as
        # the value
        #  passed to the grinder
        if self.tot_threads != self.concurrent_threads:
            raise Exception(
                "Configuration error: grinder.threads doesn't equal total "
                "concurrent threads")

        self.requests_by_type = requests_by_type

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

    def setup_thread(self, thread_num, agent_num):
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

        thread_types = [IngestThread, EnumIngestThread, QueryThread,
                        AnnotationsIngestThread]
        _thread_num = thread_num
        for x in thread_types:
            if thread_num < x.num_threads(self.config):
                thread_type = x
                break
            else:
                thread_num -= x.num_threads(self.config)

        if thread_type is None:
            raise Exception("Invalid Thread Type")

        if thread_type is QueryThread:
            # query threads will look up by query type
            query_types = [
                SinglePlotQuery,
                MultiPlotQuery,
                SearchQuery,
                EnumSearchQuery,
                EnumSinglePlotQuery,
                AnnotationsQuery,
                EnumMultiPlotQuery,
            ]
            query_type = SinglePlotQuery
            n = _thread_num
            for qt in query_types:
                if n < qt.get_num_queries_for_current_node(agent_num, self.config):
                    query_type = qt
                    break
                n -= qt.get_num_queries_for_current_node(agent_num, self.config)
            req = self.requests_by_type[query_type]
            query = query_type(0, agent_num, QueryThread.num_threads(self.config), self.config, req)
            return query
        elif thread_type in self.requests_by_type:
            req = self.requests_by_type[thread_type]
            return thread_type(thread_num, agent_num, req, self.config)
        else:
            raise TypeError("Unknown thread type: %s" % str(thread_type))
