import unittest
import os


class TestResultLogMetrics(unittest.TextTestResult):
    from pathlib import Path
    metrics_log_path = None
    if os.environ.get('METRICS_LOG_PATH'):
        metrics_log_path = Path(os.environ['METRICS_LOG_PATH'])

    def addSuccess(self, test):
        super().addSuccess(test)
        if self.metrics_log_path:
            elapsed = f"{test._elapsed:.5f}" if hasattr(test, '_elapsed') else ""
            with self.metrics_log_path.open(mode='a+') as f:
                f.write(f"{test.id()}, success, {elapsed},\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.metrics_log_path:
            elapsed = f"{test._elapsed:.5f}" if hasattr(test, '_elapsed') else ""
            with self.metrics_log_path.open(mode='a+') as f:
                f.write(f"{test.id()}, fail, {elapsed}, {err}\n")

    def addError(self, test, err) -> None:
        super().addError(test, err)
        if self.metrics_log_path:
            elapsed = f"{test._elapsed:.5f}" if hasattr(test, '_elapsed') else ""
            with self.metrics_log_path.open(mode='a+') as f:
                f.write(f"{test.id()}, error, {elapsed}, {err}\n")


class TestResultCompareFileMeld(TestResultLogMetrics):
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if hasattr(test, 'out_file') and hasattr(test, 'exp_file'):
            method_id = test.id().split('.')[-1]
            if method_id in test.out_file and method_id in test.exp_file:
                cont = True
                while cont:
                    res = input("[d]iff, [c]ontinue, or [f]reeze? ")
                    if res == "f":
                        os.rename(test.out_file[method_id], test.exp_file[method_id])
                        cont = False
                    elif res == "c":
                        cont = False
                    elif res == "d":
                        os.system("meld " + str(test.exp_file[method_id]) + " " + str(test.out_file[method_id]))
