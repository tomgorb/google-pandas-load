import unittest
from tests.unit.test_getters import CallGetters

suite = unittest.TestSuite()
suite.addTest(CallGetters('test_call_loader_getters'))
suite.addTest(CallGetters('test_call_loader_quick_setup_getters'))
unittest.TextTestRunner(verbosity=2).run(suite)
