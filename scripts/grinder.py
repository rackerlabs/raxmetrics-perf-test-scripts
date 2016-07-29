from net.grinder.script.Grinder import grinder
import ingest
import ingestenum
import annotationsingest
import query
import thread_manager as tm
import py_java

# ENTRY POINT into the Grinder

# The code inside the TestRunner class is gets executed by each worker thread
# Outside the class is executed before any of the workers begin


class TestRunner:
    def __init__(self):
        config = py_java.get_config_from_grinder(grinder)
        thread_manager = tm.ThreadManager(config)
        thread_manager.create_all_metrics(grinder.getAgentNumber())
        self.thread = thread_manager.setup_thread(grinder.getThreadNumber())

    def __call__(self):
        result = self.thread.make_request(grinder.logger.info)
