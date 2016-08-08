#!/usr/bin/env python

import random
import time

default_config = {
    'name_fmt': "org.example.metric.%d",
    'report_interval': (1000 * 10),
    'annotations_num_tenants': 5,
    'num_tenants': 4,
    'enum_num_tenants': 4,
    'metrics_per_tenant': 15,
    'enum_metrics_per_tenant': 10,
    'annotations_per_tenant': 10,
    'ingest_batch_size': 5,
    'enum_batch_size': 5,
    'ingest_weight': 15,
    'enum_ingest_weight': 15,
    'num_nodes': 1,
    'url': "http://localhost:19000",
    'query_url': "http://localhost:20000",
    'query_concurrency': 10,
    'annotations_weight': 5,
    'max_multiplot_metrics': 10,
    'search_query_weight': 10,
    'enum_search_query_weight': 10,
    'enum_single_plot_query_weight': 10,
    'multiplot_query_weight': 10,
    'enum_multiplot_query_weight': 10,
    'enum_num_values': 10,
    'singleplot_query_weight': 10,
    'annotations_query_weight': 8,
    # ingest_delay_millis is comma separated list of delays used during
    # ingestion
    'ingest_delay_millis': ""}


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
