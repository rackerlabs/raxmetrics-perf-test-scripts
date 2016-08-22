#!/usr/bin/env python

from __future__ import with_statement
import threading
import time


class ThrottlingGroup(object):

    """Throttling groups allow you to limit the number of requests made by
     threads. Separate threads can share a single ThrottlingGroup object, so
     that they all count towards the limit. If a request puts a given
     throttling group over its limit, then the thread that is trying to send
     the request will sleep until the 1-minute interval has completed. All
     other threads that attempt to send a request during that time will block.
    """

    def __init__(self, name, max_requests_per_minute, time_source=None,
                 sleep_source=None):

        if time_source is None:
            time_source = time.time
        if sleep_source is None:
            sleep_source = time.sleep

        self.name = name
        self.max_requests_per_minute = max_requests_per_minute
        self.count = 0
        self.lock = threading.Lock()
        self.start_time = -1
        self.time_source = time_source
        self.sleep_source = sleep_source

    def count_request(self):
        with self.lock:
            current_time = self.time_source()
            if self.start_time < 0:
                self.count += 1
                self.start_time = current_time
                return

            seconds_since_start = current_time - self.start_time
            if seconds_since_start >= 60:
                self.count = 1
                self.start_time = current_time
            elif self.count < self.max_requests_per_minute:
                self.count += 1
            else:
                seconds_to_wait = self.start_time + 60 - current_time
                if seconds_to_wait > 0:
                    self.sleep_source(seconds_to_wait)
                self.count = 1
                self.start_time = self.time_source()


class NullThrottlingGroup(object):
    def count_request(self):
        pass
