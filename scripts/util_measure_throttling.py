#!/usr/bin/env python

import threading
import time
import locale
import argparse
import logging

from throttling_request import ThrottlingRequest
from throttling_group import ThrottlingGroup

locale.setlocale(locale.LC_ALL, 'en_US')


class MeasuringRequest(object):
    count = 0
    last_t = 0
    rpm = 0
    start_time = 0

    def __init__(self, sleep_seconds=None, report_seconds=None):
        self.reset()
        self.sleep_seconds = sleep_seconds
        if report_seconds is None:
            report_seconds = 1
        self.report_seconds = report_seconds

    def reset(self):
        self.count = 0
        self.last_t = time.time()

    def GET(self, *args, **kwargs):
        if self.sleep_seconds:
            time.sleep(self.sleep_seconds)
        self.count += 1
        t = time.time()
        delta = t - self.last_t
        if delta > self.report_seconds:
            self.rpm = self.count * 60 / delta
            self.count = 0
            self.last_t = t
            print(
                ("%f seconds elapsed, running at about " % (t -
                                                            self.start_time)) +
                locale.format("%d", self.rpm, grouping=True) +
                " requests per minute.")

    def start(self):
        self.start_time = time.time()

    def finish(self):
        t = time.time()
        delta = t - self.last_t
        self.rpm = self.count * 60 / delta
        print(
            ("%f seconds elapsed, running at about " % (t -
                                                        self.start_time)) +
            locale.format("%d", self.rpm, grouping=True) +
            " requests per minute.")


def loop(start_time, req, run_seconds):
    while True:
        req.GET()
        t = time.time()
        if t - start_time > run_seconds:
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-seconds', type=float, default=180,
                        help='How long to run the test.')
    parser.add_argument('--max-rpm', type=int, default=1000,
                        help='Maximum requests per minute')
    parser.add_argument('--log', action='store_true',
                        help='Print additional diagnostic information.')
    parser.add_argument('--threads', action='store', type=int, default=1,
                        help='The number of threads to make requests with.')
    parser.add_argument('--no-throttling', action='store_true',
                        help='Turn off throttling completely. Requests will '
                             'run as fast as possible. This causes the '
                             'program to ignore the --max-rpm argument.')
    parser.add_argument('--sleep-seconds', type=float,
                        help='time in seconds to sleep at the beginning of '
                             'the GET method.')
    parser.add_argument('--report-seconds', type=float, default=1,
                        help='Time in seconds in between reporting estimated '
                             'average requests per second.')

    args = parser.parse_args()

    if args.log:
        logging.basicConfig(
            format="%(asctime)-15s %(thread)d %(method)-32s %(message)s",
            level=logging.INFO)

    max_rpm = args.max_rpm
    run_seconds = args.run_seconds
    sleep_seconds = args.sleep_seconds
    report_seconds = args.report_seconds
    no_throttling = args.no_throttling
    num_threads = args.threads

    print('Max requests per minute: %s' % str(max_rpm))
    print('Run length in seconds: %s' % str(run_seconds))
    print('Sleep length in seconds: %s' % str(sleep_seconds))
    print('Report numbers every %s seconds' % str(report_seconds))
    print('Throttling is %s' % ('disabled' if no_throttling else 'enabled'))
    print('Number of threads: %s' % str(num_threads))

    req0 = MeasuringRequest(sleep_seconds=sleep_seconds,
                            report_seconds=report_seconds)

    tgroup = ThrottlingGroup('name', max_rpm)
    print('tgroup.seconds_per_request: %s' % float(tgroup.seconds_per_request))
    if no_throttling:
        req = req0
    else:
        req = ThrottlingRequest(tgroup, req0)

    start_time = time.time()
    req0.start()
    threads = []
    for i in xrange(num_threads):
        th = threading.Thread(target=loop, name='thread-{}'.format(i),
                              args=(start_time, req, run_seconds))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

    req0.finish()

if __name__ == '__main__':
    main()
