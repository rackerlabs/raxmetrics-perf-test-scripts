#!/usr/bin/env python

import ast

import java.util.Properties
from net.grinder.script.Grinder import ScriptContext
import net.grinder.engine.process.ScriptContextImplementation

import py_java
from abstract_thread import default_config

class ThreadManager(object):
    # keep track of the various thread types
    types = []

    @classmethod
    def add_type(cls, type):
        cls.types.append(type)

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

    def setup_config(self, grinder):
        if py_java.is_java_object(grinder):
            if isinstance(grinder, ScriptContext):
                grinder = py_java.dict_from_properties(grinder.getProperties())
            elif type(grinder) == \
                    net.grinder.engine.process.ScriptContextImplementation:
                grinder = py_java.dict_from_properties(grinder.getProperties())
            elif isinstance(grinder, java.lang.Properties):
                grinder = py_java.dict_from_properties(grinder)
            else:
                raise TypeError("Unknown configuration object type")

        # Parse the properties file and update default_config dictionary
        for k, v in grinder.iteritems():
            if v.startswith(".."):
                continue
            if k == "grinder.threads":
                self.tot_threads = self.convert(v)
            if k.find("concurrency") >= 0:
                self.concurrent_threads += self.convert(v)
            if not k.startswith("grinder.bf."):
                continue
            k = k.replace("grinder.bf.", "")
            default_config[k] = self.convert(v)

    def __init__(self, grinder):
        # tot_threads is the value passed to the grinder at startup for the
        # number of threads to start
        self.tot_threads = 0

        # concurrent_threads is the sum of the various thread types, (currently
        # ingest and query)
        self.concurrent_threads = 0
        self.setup_config(grinder)

        # Sanity check the concurrent_threads to make sure they are the same as
        # the value
        #  passed to the grinder
        if self.tot_threads != self.concurrent_threads:
            raise Exception(
                "Configuration error: grinder.threads doesn't equal total concurrent threads")

    def create_all_metrics(self, agent_number):
        """Step through all the attached types and have them create their
        metrics"""
        for x in self.types:
            x.create_metrics(agent_number)

    def setup_thread(self, thread_num):
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
        server_num = thread_num

        for x in self.types:
            if server_num < x.num_threads():
                thread_type = x
                break
            else:
                server_num -= x.num_threads()

        if thread_type == None:
            raise Exception("Invalid Thread Type")

        return thread_type(server_num)
