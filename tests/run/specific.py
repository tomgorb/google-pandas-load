import unittest
from tests.unit.test_raise_error import LoadRaiseErrorTest

suite = unittest.TestSuite()
suite.addTest(LoadRaiseErrorTest('test_raise_error_if_no_configs'))
unittest.TextTestRunner(verbosity=2).run(suite)
