#!/usr/bin/env python

import random
import time

default_config = {
    'name_fmt': "t4.int.abcdefg.hijklmnop.qrstuvw.xyz.ABCDEFG.HIJKLMNOP.QRSTUVW.XYZ.abcdefg.hijklmnop.qrstuvw.xyz.met.%d",
    'report_interval': (1000 * 10),
    'annotations_num_tenants': 5,
    'num_tenants': 4,
    'enum_num_tenants': 4,
    'metrics_per_tenant': 15,
    'enum_metrics_per_tenant': 10,
    'annotations_per_tenant': 10,
    'batch_size': 5,
    'ingest_concurrency': 15,
    'enum_ingest_concurrency': 15,
    'num_nodes': 1,
    'url': "http://localhost:19000",
    'query_url': "http://localhost:20000",
    'query_concurrency': 10,
    'annotations_concurrency': 5,
    'max_multiplot_metrics': 10,
    'search_queries_per_interval': 10,
    'enum_search_queries_per_interval': 10,
    'enum_single_plot_queries_per_interval': 10,
    'multiplot_per_interval': 10,
    'enum_multiplot_per_interval': 10,
    'enum_num_values': 10,
    'singleplot_per_interval': 10,
    'annotations_queries_per_interval': 8,
    # ingest_delay_millis is comma separated list of delays used during
    # ingestion
    'ingest_delay_millis': ""}

units_map = {0: 'minutes',
             1: 'hours',
             2: 'days',
             3: 'months',
             4: 'years',
             5: 'decades'}


class AbstractThread(object):
    # superclass for the various thread types
    @classmethod
    def create_metrics(cls, agent_number):
        raise Exception("Can't create abstract thread")

    @classmethod
    def num_threads(cls):
        raise Exception("Can't create abstract thread")

    def make_request(self, logger):
        raise Exception("Can't create abstract thread")

    def __init__(self, thread_num, config):
        # The threads only do so many invocations for each 'report_interval'
        # position refers to the current position for current interval
        self.position = 0

        self.config = default_config.copy()
        if config:
            self.config.update(config)

        # finish_time is the end time of the interval
        self.finish_time = self.time() + self.config['report_interval']

    def generate_unit(self, tenant_id):
        unit_number = tenant_id % 6
        return units_map[unit_number]

    def check_position(self, logger, max_position):
        """Sleep if finished all work for report interval"""
        if self.position >= max_position:
            self.position = 0
            sleep_time = self.finish_time - self.time()
            self.finish_time += self.config['report_interval']
            if sleep_time < 0:
                # return error
                logger("finish time error")
            else:
                logger("pausing for %d" % sleep_time)
                self.sleep(sleep_time)

    @classmethod
    def time(cls):
        return int(time.time() * 1000)

    @classmethod
    def sleep(cls, x):
        return time.sleep(x / 1000)


def generate_job_range(total_jobs, total_servers, server_num):
    """ Determine which subset of the total work the current server is to
    do.

    The properties file is the same for all the distributed workers and
    lists the total amount of work to be done for each report interval.
    This method allows you to split that work up into the exact subset to
    be done by the "server_num" worker
    """
    jobs_per_server = total_jobs / total_servers
    remainder = total_jobs % total_servers
    start_job = jobs_per_server * server_num
    start_job += min(remainder, server_num)
    end_job = start_job + jobs_per_server
    if server_num < remainder:
        end_job += 1
    return (start_job, end_job)


def generate_metrics_tenants(num_tenants, metrics_per_tenant,
                             agent_number, num_nodes, gen_fn):
    """generate the subset of the total metrics to be done by this agent"""
    tenants_in_shard = range(
        *generate_job_range(num_tenants, num_nodes, agent_number))
    metrics = []
    for y in map(lambda x: gen_fn(x, metrics_per_tenant),
                 tenants_in_shard):
        metrics += y
    random.shuffle(metrics)
    return metrics


def generate_metric_name(metric_id, config=default_config):
    return config['name_fmt'] % metric_id


# TODO: Add enum prefix to config
def generate_enum_metric_name(metric_id, config=default_config):
    return "enum_grinder_" + config['name_fmt'] % metric_id
