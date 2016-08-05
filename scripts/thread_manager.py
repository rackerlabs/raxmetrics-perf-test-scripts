#!/usr/bin/env python

import ast

from abstract_thread import default_config
from annotationsingest import AnnotationsIngestThread
from ingest import IngestThread
from ingestenum import EnumIngestThread
from query import SinglePlotQuery, MultiPlotQuery, SearchQuery
from query import EnumSearchQuery, EnumSinglePlotQuery, AnnotationsQuery
from query import EnumMultiPlotQuery
from config import clean_configs


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
        for k, v in clean_configs(config).iteritems():
            if str(v).startswith(".."):
                continue
            if k == "grinder.threads":
                self.tot_threads = self.convert(v)
            k = k.replace("grinder.bf.", "")
            self.config[k] = self.convert(v)

        self.concurrent_threads = (
            self.config.get('ingest_concurrency', 0) +
            self.config.get('enum_ingest_concurrency', 0) +
            self.config.get('annotations_concurrency', 0) +
            self.config.get('search_queries_per_interval', 0) +
            self.config.get('enum_search_query_weight', 0) +
            self.config.get('multiplot_query_weight', 0) +
            self.config.get('singleplot_query_weight', 0) +
            self.config.get('enum_single_plot_query_weight', 0) +
            self.config.get('enum_multiplot_query_weight', 0))

        # Sanity check the concurrent_threads to make sure they are the same as
        # the value
        #  passed to the grinder
        if self.tot_threads != self.concurrent_threads:
            raise Exception(
                "Configuration error: grinder.threads (%s) doesn't equal total"
                " concurrent threads (%s)" %
                (self.tot_threads, self.concurrent_threads))

        self.requests_by_type = requests_by_type

    def convert(self, s):
        try:
            return int(s)
        except:
            pass
        if isinstance(s, basestring):
            if len(s) > 0 and s[0] in ("'", '"'):
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

        thread_types = [IngestThread, EnumIngestThread, SinglePlotQuery,
                        MultiPlotQuery, SearchQuery, EnumSearchQuery,
                        EnumSinglePlotQuery, AnnotationsQuery,
                        EnumMultiPlotQuery, AnnotationsIngestThread]
        for x in thread_types:
            if thread_num < x.num_threads(self.config):
                thread_type = x
                break
            else:
                thread_num -= x.num_threads(self.config)

        if thread_type is None:
            raise Exception("Invalid Thread Type")

        if thread_type in self.requests_by_type:
            req = self.requests_by_type[thread_type]
            return thread_type(thread_num, agent_num, req, self.config)
        else:
            raise TypeError("Unknown thread type: %s" % str(thread_type))
