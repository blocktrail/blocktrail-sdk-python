import unittest
from tests import cross_platform_test, api_client_test

alltests = unittest.TestSuite((cross_platform_test.CrossPlatformTestCase(), api_client_test.ApiClientTestCase(), ))

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(alltests)
