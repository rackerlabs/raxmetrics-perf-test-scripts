#!/usr/bin/env python

import time
import locale
import argparse

from throttling_request import ThrottlingRequest
from throttling_group import ThrottlingGroup

locale.setlocale(locale.LC_ALL, 'en_US')


class MeasuringRequest(object):
    count = 0
    last_t = 0
    rpm = 0

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
            print(locale.format("%d", self.rpm, grouping=True) +
                  " requests per minute")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-seconds', type=float, default=180,
                        help='How long to run the test.')
    parser.add_argument('--max-rpm', type=int, default=1000,
                        help='Maximum requests per minute')

    args = parser.parse_args()

    req0 = MeasuringRequest()

    tgroup = ThrottlingGroup('name', args.max_rpm)
    req = ThrottlingRequest(tgroup, req0)

    start_time = time.time()
    while True:
        req.GET()
        t = time.time()
        if t - start_time > args.run_seconds:
            break


if __name__ == '__main__':
    main()
