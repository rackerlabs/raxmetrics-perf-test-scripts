#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser(
    description='Read through grinder data log files and calculate '
                'statistics about various request types.')
parser.add_argument('--start-time-ms', default=0)
parser.add_argument('--stop-time-ms', default=2000000000000)
# 2000000000000ms --> May 17th, 2033 at 10:33:20 PM
parser.add_argument('log_files', nargs='+', metavar='log-files')

args = parser.parse_args()

print('Start time: {} ms'.format(args.start_time_ms))
print('Stop time: {} ms'.format(args.stop_time_ms))

start_time = int(args.start_time_ms)
stop_time = int(args.stop_time_ms)


class Test(object):
    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.count = 0
        self.success_count = 0

tests = {
    1: Test('Ingest', 1),
    2: Test('Annotations Ingest', 2),
    3: Test('SinglePlot Query', 3),
    4: Test('MultiPlot Query', 4),
    5: Test('Search Query', 5),
    6: Test('Annotations Query', 6),
}

first_line = ''
first_line_number = 'none'
last_line = ''
last_line_number = 'none'


def clean_int(x):
    return int(x.strip())

def percent(x, n):
    try:
        return int(round(100 * x / n))
    except:
        return float('nan')

print args
for log_file in args.log_files:
    with open(log_file) as f:
        header = f.readline()
        total_lines = 1
        for line in f.readlines():
            total_lines += 1
            (thread, run, test_number, test_start_time, test_time, errors, response_code,
             response_length, response_errors, time_to_resolv, time_to_connect,
             time_to_first_byte, new_conns) = map(clean_int, line.split(','))
            if start_time <= test_start_time < stop_time:
                if not first_line:
                    first_line = line
                    first_line_number = total_lines

                try:
                    test = tests[test_number]
                except KeyError:
                    test = Test('Test {}'.format(test_number), test_number)
                    tests[test_number] = test

                test.count += 1

                if int(errors) < 1:
                    test.success_count += 1

                last_line = line
                last_line_number = total_lines

    sorted_tests = [tests[i] for i in sorted(tests.iterkeys())]
    total = sum(t.count for t in sorted_tests)
    total_successes = sum(t.success_count for t in sorted_tests)

    print('Log file: {}'.format(log_file))

    print('  Totals: {}'.format(total))
    for test in sorted_tests:
        print('    {} ({}): {} ({}% of all requests)'.format(
            test.name, test.number, test.count, percent(test.count, total)))

    print('  Successes: {}'.format(total_successes))
    for test in sorted_tests:
        template = ('    {} ({}): {} ({}% of all successful requests,'
                    ' {}% success rate for this test)')
        print(template.format(test.name, test.number, test.success_count,
                              percent(test.success_count, total_successes),
                              percent(test.success_count, test.count)))

    print('')
    print('  Total lines: {}'.format(total_lines))
    print('  First line: "{}" ({})'.format(first_line.strip(), first_line_number))
    print('  Last line: "{}" ({})'.format(last_line.strip(), last_line_number))
