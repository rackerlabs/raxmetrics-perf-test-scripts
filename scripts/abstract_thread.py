#!/usr/bin/env python

import random
import time

default_config = {
    'url': "http://localhost:19000",
    'query_url': "http://localhost:20000",

    'name_fmt': "org.example.metric.%d",
    'max_multiplot_metrics': 10,


    'ingest_weight': 15,
    'ingest_num_tenants': 4,
    'ingest_metrics_per_tenant': 15,
    'ingest_batch_size': 5,
    # ingest_delay_millis is comma separated list of delays used during
    # ingestion
    'ingest_delay_millis': "",

    'enum_ingest_weight': 0,
    'enum_num_tenants': 4,
    'enum_metrics_per_tenant': 10,
    'enum_batch_size': 5,
    'enum_num_values': 10,

    'annotations_weight': 5,
    'annotations_num_tenants': 5,
    'annotations_per_tenant': 10,

    'singleplot_query_weight': 10,

    'multiplot_query_weight': 10,

    'search_query_weight': 10,

    'enum_search_query_weight': 0,

    'enum_single_plot_query_weight': 0,

    'enum_multiplot_query_weight': 0,

    'annotations_query_weight': 8}


class AbstractThread(object):
    # superclass for the various thread types

    def make_request(self, logger, time):
        raise Exception("Can't create abstract thread")

    def __init__(self, thread_num, agent_num, request, config):

        self.thread_num = thread_num
        self.agent_num = agent_num
        self.request = request

        self.config = default_config.copy()
        if config:
            self.config.update(config)

    @classmethod
    def time(cls):
        return int(time.time() * 1000)

    @classmethod
    def sleep(cls, x):
        return time.sleep(x / 1000)


def generate_metric_name(metric_id, config):
    return config['name_fmt'] % metric_id
