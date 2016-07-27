import random

from abstract_thread import default_config


RAND_MAX = 982374239



# ThreadManager class ends here
# Utility functions below

def generate_job_range(total_jobs, total_servers, server_num):
    """ Determine which subset of the total work the current server is to do.

    The properties file is the same for all the distributed workers and lists
    the total amount of work to be done for each report interval.  This method
    allows you to split that work up into the exact subset to be done by the
    "server_num" worker
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
    """ generate the subset of the total metrics to be done by this agent"""
    tenants_in_shard = range(
        *generate_job_range(num_tenants, num_nodes, agent_number))
    metrics = []
    for y in map(lambda x: gen_fn(x, metrics_per_tenant), tenants_in_shard):
        metrics += y
    random.shuffle(metrics)
    return metrics


def generate_metric_name(metric_id):
    return default_config['name_fmt'] % metric_id


# TODO: Add enum prefix to config
def generate_enum_metric_name(metric_id):
    return "enum_grinder_" + default_config['name_fmt'] % metric_id


# Utility functions end here
