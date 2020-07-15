import argparse
import logging
import logging.handlers
import os
import sys
import time
import unittest
from pathlib import Path

from .results import TestResultLogMetrics, TestResultCompareFileMeld
from . import TEST_DIR_PATH


class TestParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"error: {message}\n")
        self.print_help()
        sys.exit(2)

    @staticmethod
    def is_not_suite(test: unittest.suite.TestSuite):
        try:
            iter(test)
        except TypeError:
            return True
        return False

    @staticmethod
    def discover_test_suites(starting_dir: Path):
        checking_dirs = {starting_dir}
        suites_dir = set()
        while checking_dirs:
            checking_d = checking_dirs.pop()
            sub_dirs = {d for d in checking_d.iterdir() if d.is_dir() and d.stem != '__pycache__'}
            if not sub_dirs:
                suites_dir.add(checking_d)
            else:
                checking_dirs = checking_dirs.union(sub_dirs)
        test_suites = {}
        for d in suites_dir:
            tests = unittest.TestLoader().discover(str(d))
            if tests.countTestCases() > 0:
                test_suites['.'.join(d.relative_to(starting_dir).parts)] = tests
        return test_suites

    def discover_test_methods(self, starting_dir: Path):
        discovered_tests = unittest.TestLoader().discover(str(starting_dir))

        def test_case_gen(t_suite):
            for test in t_suite:
                if self.is_not_suite(test):
                    yield test.id()
                else:
                    for t in test_case_gen(test):
                        yield t

        return sorted(list(test_case_gen(discovered_tests)))

    def discover_test_cases(self, starting_dir: Path):
        discovered_tests = unittest.TestLoader().discover(str(starting_dir))

        def test_case_gen(t_suite):
            for test in t_suite:
                if self.is_not_suite(test):
                    case = '.'.join(test.id().split('.')[:-1])
                    yield case
                else:
                    for t in test_case_gen(test):
                        yield t

        return sorted(list(set(test_case_gen(discovered_tests))))

    def __init__(self):
        super().__init__()
        self.prog = 'tests'
        self.epilog = """example:
        tests all
        tests all -d path/to/testDir
        tests list suite | case | method
        tests suite testSuite --quiet --meld
        tests case suiteName.caseName
        tests case suiteName.caseName.caseClass.methodName
        """
        self.add_argument(
            '-l', '--logDirPath', type=str, default='.logs',
            help=f"Path to log dir containing debug log (default: .logs)"
        )
        self.add_argument('-s', '--logStdout', action='store_true', help='log to stdout as well as to a log file')
        self.add_argument(
            '-q', '--quiet', action='store_true',
            help=f"Set logging level as INFO (default: False)"
        )
        self.add_argument('--meld', action='store_true', help='Use meld to compare out and exp file (default False)')
        sub_parser = self.add_subparsers(
            title='command', dest='command', metavar='<command>', parser_class=argparse.ArgumentParser
        )
        sub_parser.required = True
        suite_parser = sub_parser.add_parser('suite', help='Run a test suite')
        suite_parser.add_argument('suiteName', type=str, help=f"Name of the suite to be run")
        case_parser = sub_parser.add_parser('case', help='Run a test case or method')
        case_parser.add_argument('caseName', type=str,
                                 help="Path to TestCase or method from the testDir separated by dot")
        sub_parser.add_parser('all', help='Test all cases discovered from the testDir ')
        list_parser = sub_parser.add_parser(
            'list', help='List discovered test suites or cases or methods from the testDir'
        )
        list_parser.add_argument('level', type=str, choices=['suite', 'case', 'method'])

    def __call__(self):
        args = self.parse_args()
        log_dir = TEST_DIR_PATH.joinpath(args.logDirPath)
        log_dir.mkdir(exist_ok=True)

        os.environ['METRICS_LOG_PATH'] = str(log_dir / 'test_metrics.log')
        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_dir / 'test.log'), maxBytes=10 * 1024 * 1024, backupCount=5
        )
        log_config_kwargs = {
            'format': '%(asctime)s %(name)-20s %(levelname)-10s %(message)s',
            'datefmt': "%Y-%m-%dT%H:%M:%S%z",
            'handlers': [file_handler, logging.StreamHandler()]
            if args.logStdout else [file_handler]
        }

        if args.quiet:
            log_config_kwargs['level'] = logging.INFO
            verbosity = 1
        else:
            log_config_kwargs['level'] = logging.DEBUG
            verbosity = 2
        logging.basicConfig(**log_config_kwargs)
        logging.Formatter.converter = time.gmtime

        result_class = TestResultCompareFileMeld if args.meld else TestResultLogMetrics
        runner = unittest.TextTestRunner(verbosity=verbosity, resultclass=result_class)

        all_succeed = True
        test_suites = self.discover_test_suites(TEST_DIR_PATH)
        if args.command == 'all':
            results = [runner.run(test_suites[s_name]).wasSuccessful() for s_name in test_suites]
            all_succeed = all(results)
        elif args.command == 'suite':
            if args.suiteName in list(test_suites.keys()):
                all_succeed = runner.run(test_suites[args.suiteName]).wasSuccessful()
            else:
                self.error(f"Suite {args.suiteName} not found in {TEST_DIR_PATH}. Use `list` option to list suite")
        elif args.command == 'case':
            relative_to_root = '.'.join(TEST_DIR_PATH.relative_to(os.getcwd()).parts)
            suite = unittest.defaultTestLoader.loadTestsFromName(f"{relative_to_root}.{args.caseName}")
            all_succeed = runner.run(suite).wasSuccessful()
        elif args.command == 'list':
            if args.level == 'suite':
                names = list(test_suites.keys())
            elif args.level == 'case':
                names = self.discover_test_cases(TEST_DIR_PATH)
            else:
                names = self.discover_test_methods(TEST_DIR_PATH)
            if not names:
                sys.stdout.write(f"No {args.level} found in {TEST_DIR_PATH}")
            else:
                sys.stdout.write('\n'.join(names))
                sys.stdout.write('\n')

        if not all_succeed:
            sys.exit("Some tests failed")
