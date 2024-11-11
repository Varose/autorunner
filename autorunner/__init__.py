__version__ = "1.0.1"
__description__ = "One-stop solution for AUTO testing."

# import firstly for monkey patch if needed
from autorunner.ext.locust import main_locusts
from autorunner.parser import parse_parameters as Parameters
from autorunner.runner import AutoRunner
from autorunner.testcase import Config, Step, RunRequest, RunTestCase, RunLocation

__all__ = [
    "__version__",
    "__description__",
    "AutoRunner",
    "Config",
    "Step",
    "RunLocation",
    "RunRequest",
    "RunTestCase",
    "Parameters",
    "Parameters2",
]
