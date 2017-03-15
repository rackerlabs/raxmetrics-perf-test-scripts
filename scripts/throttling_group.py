#!/usr/bin/env python

from __future__ import with_statement
import threading
import time
from Queue import Queue
import math


class ThrottlingGroup(object):
    """Throttling groups allow you to limit the number of requests made by
     generators. Separate generators can share a single ThrottlingGroup object,
     so that they all count towards the limit. The ThrottlingGroup object uses
     a background thread to coordinate the timing of requests. Requests will be
     made at an interval approximately long enough to keep the total number of
     requests for a given 60-second timespan at or below the configured limit.
     Typically, in practice, timing and calculation overhead will keep the
     number of requests at about 95% of the configured limit.
    """

    def __init__(self, name, max_requests_per_minute, time_source=None,
                 sleep_source=None):

        if time_source is None:
            time_source = time.time
        if sleep_source is None:
            sleep_source = time.sleep

        self.name = name
        self.seconds_per_request = 60 / float(max_requests_per_minute)
        self.time_source = time_source
        self.sleep_source = sleep_source
        self.q = Queue()
        self.semaphore = threading.Semaphore(0)
        self.throttler_thread = threading.Thread(target=self.__throttler,
                                                 name=name)
        self.throttler_thread.setDaemon(True)
        self.throttler_thread.start()

    def __throttler(self):
        """
        This method should not be called directly. It will be run in a separate
        thread. It synchronizes requests using a locked producer/consumer
        pattern. When another thread wants to make a request, it will call
        `q.put()` in count_request and then wait to acquire the semaphore. This
        method will then sleep for the configured amount of time, if it isn't
        already. After sleeping, it will release the semaphore, which will
        allow the other thread to continue with the request. If this method
        sleeps too long (i.e. `sleep()` is not always exact), it will release
        the semaphore multiple time to allow the other threads to catch up.
        """
        t2 = self.time_source()
        n = 0
        self.q.get()
        while True:
            self.sleep_source(self.seconds_per_request)
            t1 = self.time_source()
            delta = t1 - t2
            t2 = t1
            delta_n = delta / self.seconds_per_request
            n += delta_n
            if n >= 1:
                count = int(math.floor(n))
                n -= count
                for i in xrange(count):
                    self.semaphore.release()
                    self.q.get()

    def count_request(self):
        self.q.put(None)
        self.semaphore.acquire()


class NullThrottlingGroup(object):
    def count_request(self):
        pass
