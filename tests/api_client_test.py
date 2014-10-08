import unittest

import blocktrail


class ApiClientTestCase(unittest.TestCase):
    def setup_bad_api_client(self):
        return blocktrail.APIClient("TESTKEY-FAIL", "TESTSECRET-FAIL", debug=False)

    def setup_api_client(self):
        return blocktrail.APIClient("MYKEY", "MYSECRET", debug=True)

    def test_signing(self):
        client = self.setup_bad_api_client()

        with self.assertRaises(blocktrail.exceptions.InvalidCredentials):
            client.verify_address("16dwJmR4mX5RguGrocMfN9Q9FR2kZcLw2z", "HPMOHRgPSMKdXrU6AqQs/i9S7alOakkHsJiqLGmInt05Cxj6b/WhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk=")

        client = self.setup_api_client()
        try:
            client.verify_address("16dwJmR4mX5RguGrocMfN9Q9FR2kZcLw2z", "HPMOHRgPSMKdXrU6AqQs/i9S7alOakkHsJiqLGmInt05Cxj6b/WhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk=")
        except blocktrail.exceptions.InvalidCredentials:
            assert False, "InvalidCredentials raised"
        except Exception:
            assert True, "Other Exception is fine"

    def test_address(self):
        client = self.setup_api_client()
        address = client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")

        assert address
        assert address['address'] == "1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp"


if __name__ == "__main__":
    unittest.main()
