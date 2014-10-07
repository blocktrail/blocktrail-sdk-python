import unittest

import blocktrail


class ApiClientTestCase(unittest.TestCase):
    def setup_bad_api_client(self):
        return blocktrail.APIClient("TESTKEY-FAIL", "TESTSECRET-FAIL")

    def setup_api_client(self):
        return blocktrail.APIClient("MYKEY", "MEYSECRET")

    def test_signing(self):
        client = self.setup_bad_api_client()

        with self.assertRaises(blocktrail.exceptions.InvalidCredentials):
            client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")

        client = self.setup_api_client()
        assert client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")

    def test_address(self):
        client = self.setup_api_client()
        address = client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")

        assert address
        assert address['address'] == "1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp"
