import unittest
import hashlib
from requests.models import RequestEncodingMixin


class CrossPlatformTestCase(unittest.TestCase):
    def test_content_md5(self):
        data = {'signature': "HPMOHRgPSMKdXrU6AqQs/i9S7alOakkHsJiqLGmInt05Cxj6b/WhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk="}

        assert RequestEncodingMixin._encode_params(data) == "signature=HPMOHRgPSMKdXrU6AqQs%2Fi9S7alOakkHsJiqLGmInt05Cxj6b%2FWhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk%3D"
        assert hashlib.md5(RequestEncodingMixin._encode_params(data)).hexdigest() == "fdfc1a717d2c97649f3b8b2142507129"


