#!/usr/bin/env python

import random
import time

from throttling_group import NullThrottlingGroup
from user import NullUser

default_config = {
    'url': "http://localhost:19000",
    'query_url': "http://localhost:20000",

    'name_fmt': "org.example.metric.%d",
    'max_multiplot_metrics': 10,


    'ingest_weight': 15,
    'ingest_num_tenants': 4,
    'ingest_metrics_per_tenant': 15,
    'ingest_metrics_permutation_scale': 15,
    'ingest_batch_size': 5,
    # ingest_delay_millis is comma separated list of delays used during
    # ingestion
    'ingest_delay_millis': "",

    'annotations_weight': 5,
    'annotations_num_tenants': 5,
    'annotations_per_tenant': 10,

    'singleplot_query_weight': 10,

    'multiplot_query_weight': 10,

    'search_query_weight': 10,

    'annotations_query_weight': 8}


class AbstractGenerator(object):
    # superclass for the various generator types

    def make_request(self, logger, time):
        raise Exception("Can't create abstract generator")

    def __init__(self, thread_num, agent_num, request, config, user=None):

        self.thread_num = thread_num
        self.agent_num = agent_num
        self.request = request

        self.config = default_config.copy()
        if config:
            self.config.update(config)

        if user is None:
            user = NullUser()
        self.user = user

    @classmethod
    def time(cls):
        return int(time.time() * 1000)

    @classmethod
    def sleep(cls, x):
        return time.sleep(x / 1000)


def generate_metric_name(metric_id, config):
    name_fmt = config['name_fmt']
    dimensions = name_fmt.count('%d')
    random_values = [random.randint(1, config['ingest_metrics_permutation_scale'])
                     for _ in range(dimensions-1)]
    random_values.append(metric_id)
    format_values = tuple(random_values)
    return name_fmt % format_values
