#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--num-tests', action='store', default=6)
parser.add_argument('--start-time-ms', default=0)
parser.add_argument('--stop-time-ms', default=2000000000000)
# 2000000000000ms --> May 17th, 2033 at 10:33:20 PM
parser.add_argument('log_files', nargs='+', metavar='log-files')

args = parser.parse_args()

print('Num. tests: {}'.format(args.num_tests))
print('Start time: {} ms'.format(args.start_time_ms))
print('Stop time: {} ms'.format(args.stop_time_ms))

start_time = int(args.start_time_ms)
stop_time = int(args.stop_time_ms)
tests = [t + 1 for t in xrange(args.num_tests)]
test_counts = {t: 0 for t in tests}
test_success_counts = {t: 0 for t in tests}

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
            (thread, run, test, test_start_time, test_time, errors, response_code,
             response_length, response_errors, time_to_resolv, time_to_connect,
             time_to_first_byte, new_conns) = map(clean_int, line.split(','))
            if start_time <= test_start_time < stop_time:
                if not first_line:
                    first_line = line
                    first_line_number = total_lines

                test_counts[test] += 1
                if int(errors) < 1:
                    test_success_counts[test] += 1

                last_line = line
                last_line_number = total_lines

    total = sum(test_counts.itervalues())
    total_successes = sum(test_success_counts.itervalues())

    print('Log file: {}'.format(args.log_file))

    print('  Totals: {}'.format(total))
    for test in sorted(test_counts.iterkeys()):
        print('    {}: {} ({}% of all requests)'.format(test, test_counts[test],
                                                      percent(test_counts[test],
                                                              total)))

    print('  Successes: {}'.format(total_successes))
    for test in sorted(test_success_counts.iterkeys()):
        template = ('    {}: {} ({}% of all successful requests,'
                    ' {}% success rate for this test)')
        print(template.format(test, test_success_counts[test],
                              percent(test_success_counts[test],
                                      total_successes),
                              percent(test_success_counts[test],
                                      test_counts[test])))

    print('')
    print('  Total lines: {}'.format(total_lines))
    print('  First line: "{}" ({})'.format(first_line.strip(), first_line_number))
    print('  Last line: "{}" ({})'.format(last_line.strip(), last_line_number))
