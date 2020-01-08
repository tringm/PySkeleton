# PySkeleton
A skeleton for a generic python project

### [Test infrastructure](tests)
Based on [unittest](https://docs.python.org/3/library/unittest.html):
- Customized [TestCase](tests/utils/test_case.py) with timer, set up io folder and file compare support
- Customized [TestResult](tests/utils/test_result.py) that log metrics and interactive file compare with meld
- Customized [CLI](tests/test.py):
    - Discover suite, case, method based on hierarchy
    - Flag option for test dir, metric file, verbosity, and meld  
