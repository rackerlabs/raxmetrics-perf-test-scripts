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

        # Parse the properties file and update default_config dictionary
        self.config = default_config.copy()
        for k, v in clean_configs(config).iteritems():
            if str(v).startswith(".."):
                continue
            if k == "grinder.threads":
                self.tot_threads = self.convert(v)
            k = k.replace("grinder.bf.", "")
            self.config[k] = self.convert(v)

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
        on the "ingest_weight" and "query_concurrency" options.

        So for example, if "ingest_weight" is set to 4, and
        "query_concurrency" is set to 2, thread numbers 0-3 will be ingest
        threads and thread numbers 4-5 will be query threads.

        """
        thread_type = None

        thread_types = [
            (IngestThread, self.config['ingest_weight']),
            (EnumIngestThread, self.config['enum_ingest_weight']),
            (AnnotationsIngestThread, self.config['annotations_weight']),
            (SinglePlotQuery, self.config['singleplot_query_weight']),
            (MultiPlotQuery, self.config['multiplot_query_weight']),
            (SearchQuery, self.config['search_query_weight']),
            (EnumSearchQuery, self.config['enum_search_query_weight']),
            (EnumSinglePlotQuery,
                self.config['enum_single_plot_query_weight']),
            (EnumMultiPlotQuery, self.config['enum_multiplot_query_weight']),
            (AnnotationsQuery, self.config['annotations_query_weight']),
        ]

        total_weight = 0
        for x in thread_types:
            total_weight += x[1]

        index = int(float(total_weight) * thread_num / float(self.tot_threads))

        for x in thread_types:
            if index < x[1]:
                thread_type = x[0]
                break
            index -= x[1]

        if thread_type is None:
            raise Exception("Invalid Thread Type")

        if thread_type in self.requests_by_type:
            req = self.requests_by_type[thread_type]
            return thread_type(thread_num, agent_num, req, self.config)
        else:
            raise TypeError("Unknown thread type: %s" % str(thread_type))
