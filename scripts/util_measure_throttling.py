#!/usr/bin/env python

import time
import locale
import argparse

from throttling_request import ThrottlingRequest
from throttling_group import ThrottlingGroup, SmoothThrottlingGroup

locale.setlocale(locale.LC_ALL, 'en_US')


class MeasuringRequest(object):
    count = 0
    last_t = 0
    rpm = 0
    start_time = 0

    def __init__(self):
        self.reset()

    def reset(self):
        self.count = 0
        self.last_t = time.time()

    def GET(self, *args, **kwargs):
        self.count += 1
        t = time.time()
        delta = t - self.last_t
        if delta > 1:
            self.rpm = self.count * 60 / delta
            self.count = 0
            self.last_t = t
            print(
                ("%d seconds elapsed, running at about " % (t -
                                                            self.start_time)) +
                locale.format("%d", self.rpm, grouping=True) +
                " requests per minute")

    def start(self):
        self.start_time = time.time()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-seconds', type=float, default=180,
                        help='How long to run the test.')
    parser.add_argument('--max-rpm', type=int, default=1000,
                        help='Maximum requests per minute')
    parser.add_argument('--smooth', action='store_true',
                        help='Use the smooth throttling group, instead of the '
                             'default.')

    args = parser.parse_args()

    print('Max requests per minute: %s' % str(args.max_rpm))
    print('Run length in seconds: %s' % str(args.run_seconds))
    if args.smooth:
        print('Throttling group type: smooth')
    else:
        print('Throttling group type: default')

    req0 = MeasuringRequest()

    if args.smooth:
        tgroup = SmoothThrottlingGroup('name', args.max_rpm)
    else:
        tgroup = ThrottlingGroup('name', args.max_rpm)
    req = ThrottlingRequest(tgroup, req0)

    start_time = time.time()
    req0.start()
    while True:
        req.GET()
        t = time.time()
        if t - start_time > args.run_seconds:
            break


if __name__ == '__main__':
    main()
