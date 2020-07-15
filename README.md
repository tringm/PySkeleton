# PySkeleton
A skeleton for a generic python project

### [Test infrastructure](tests)
Based on [unittest](https://docs.python.org/3/library/unittest.html):
- Customized [TestCase](tests/cases.py) with timer, set up io folder and file comparison support
- Customized [TestResult](tests/results.py) that log metrics and interactive file compare with meld
- Customized [Test CLI](tests/parser.py):
    - Discover suite, case, method based on hierarchy
    - Flag option for test dir, metric file, verbosity, and meld  

**To add a test suite, simply add a new package in the `tests` package and add test cases there**

### [Utils pacakge](utils)
- [Logging utils](utils/logging.py)
- A versatile [ArgParser](utils/parser.py) on top of argparse.ArgumentParser