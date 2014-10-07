import unittest

import src
from src.connection import InvalidCredentials


class ApiClientTestCase(unittest.TestCase):
    def runTest(self):
        self.test_signing()
        self.test_address()

    def setup_bad_api_client(self):
        return src.APIClient("TESTKEY-FAIL", "TESTSECRET-FAIL")

    def setup_api_client(self):
        return src.APIClient("MYKEY", "MEYSECRET")

    def test_signing(self):
        client = self.setup_bad_api_client()

        try:
            client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")
            assert False, "Bad key still succeeds"
        except InvalidCredentials:
            assert True, "Bad keys will fail"

        client = self.setup_api_client()
        assert client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")

    def test_address(self):
        client = self.setup_api_client()
        address = client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")

        assert address
        assert address['address'] == "1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp"
