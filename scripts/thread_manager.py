#!/usr/bin/env python

import ast

from abstract_thread import default_config
from annotationsingest import AnnotationsIngestGenerator
from ingest import IngestGenerator
from query import SinglePlotQueryGenerator, MultiPlotQueryGenerator, SearchQueryGenerator
from query import AnnotationsQuery
from config import clean_configs, convert


class ThreadManager(object):
    # keep track of the various thread types
    thread_types = []

    def __init__(self, config, requests_by_type):
        # tot_threads is the value passed to the grinder at startup for the
        # number of threads to start
        self.tot_threads = 0

        self.config = default_config.copy()
        self.config.update(clean_configs(config))
        if 'grinder.threads' in self.config:
            self.tot_threads = convert(self.config['grinder.threads'])

        self.requests_by_type = requests_by_type

    def setup_thread(self, thread_num, agent_num, tgroups=None, user=None):
        """Figure out which type thread to create based on thread_num and
        return it

        Creates threads of various types for use by the grinder to load
        test various parts of blueflood.  The code is structured so that
        the thread type is determined by the thread num.  The grinder
        properties file determines how many of each type to create based
        on the "*_weight" options.

        So for example, if "grinder.threads" is set to 8, "ingest_weight" is
        set to 4, "singleplot_query_weight" is set to 4, and all other
        "*_weight" properties are set to 0, threads numbered 0-3 will be
        IngestThread's, and threads numbered 4-7 will be SinglePlotQuery's.
        The weight numbers are proportional, so they don't have to add up
        exactly. If "grinder.threads" is set to 8, "ingest_weight" is set to
        15, "singleplot_query_weight" is set to 5, and all other "*_weight"
        properties are set to 0, then threads 0-5 will be IngestThread's, and
        threads 6 and 7 will be SinglePlotQuery's
        (15 + 5 = 20, 15 -> 75%, 5 -> 25%).

        """
        thread_type = None

        thread_types = [
            (IngestGenerator, self.config['ingest_weight'],
             self.config.get('ingest_throttling_group', None)),
            (AnnotationsIngestGenerator, self.config['annotations_weight'],
             self.config.get('annotations_throttling_group', None)),
            (SinglePlotQueryGenerator, self.config['singleplot_query_weight'],
             self.config.get('singleplot_query_throttling_group', None)),
            (MultiPlotQueryGenerator, self.config['multiplot_query_weight'],
             self.config.get('multiplot_query_throttling_group', None)),
            (SearchQueryGenerator, self.config['search_query_weight'],
             self.config.get('search_query_throttling_group', None)),
            (AnnotationsQuery, self.config['annotations_query_weight'],
                self.config.get('annotations_query_throttling_group', None)),
        ]

        total_weight = 0
        for type, weight, tgname in thread_types:
            total_weight += weight

        index = int(float(total_weight) * thread_num / float(self.tot_threads))

        for thread_type, weight, tgname in thread_types:
            if index < weight:
                break
            index -= weight

        if thread_type is None:
            raise Exception("Invalid Thread Type")

        if thread_type in self.requests_by_type:
            req = self.requests_by_type[thread_type]
            tgroup = None
            if tgname and tgroups and tgname in tgroups:
                tgroup = tgroups[tgname]
            return thread_type(thread_num, agent_num, req, self.config, user)
        else:
            raise TypeError("Unknown thread type: %s" % str(thread_type))
