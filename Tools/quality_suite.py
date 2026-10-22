"""Isolated unittest worker for quality_check. Laptop only; never installs packages."""
import argparse
import json
from pathlib import Path
import sys
import unittest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', required=True, type=Path)
    parser.add_argument('--result', required=True, type=Path)
    args = parser.parse_args(argv)
    suite = unittest.defaultTestLoader.discover(str(args.start.resolve()), pattern='test*.py')
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=1).run(suite)
    successful = result.wasSuccessful() and result.testsRun > 0
    value = {'schema_version': 1, 'tests_run': result.testsRun,
             'failures': [{'test': str(test), 'traceback': trace} for test, trace in result.failures],
             'errors': [{'test': str(test), 'traceback': trace} for test, trace in result.errors],
             'skipped': [{'test': str(test), 'reason': reason} for test, reason in result.skipped],
             'unexpected_successes': [str(test) for test in result.unexpectedSuccesses],
             'expected_failures': [str(test) for test, trace in result.expectedFailures],
             'successful': successful,
             'reason': None if result.testsRun else 'No tests were discovered; empty suites do not pass.'}
    args.result.write_text(json.dumps(value, indent=2), encoding='utf8')
    return 0 if successful else 1


if __name__ == '__main__':
    sys.exit(main())
