import unittest
import hashlib


try:
    import httpsig_cffi as sign
    from httpsig_cffi.utils import parse_authorization_header
except:
    import httpsig as sign
    from httpsig.utils import parse_authorization_header

from requests.models import RequestEncodingMixin


class CrossPlatformTestCase(unittest.TestCase):
    def test_content_md5(self):
        data = {'signature': "HPMOHRgPSMKdXrU6AqQs/i9S7alOakkHsJiqLGmInt05Cxj6b/WhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk="}

        assert RequestEncodingMixin._encode_params(data) == "signature=HPMOHRgPSMKdXrU6AqQs%2Fi9S7alOakkHsJiqLGmInt05Cxj6b%2FWhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk%3D"
        assert hashlib.md5(RequestEncodingMixin._encode_params(data).encode("utf-8")).hexdigest() == "fdfc1a717d2c97649f3b8b2142507129"

    def test_hmac(self):
        hs = sign.HeaderSigner(key_id='pda', algorithm='hmac-sha256', secret='secret', headers=['(request-target)', 'Date'])
        unsigned = {
            'Date': 'today',
            'accept': 'llamas'
        }
        signed = hs.sign(unsigned, method='GET', path='/path?query=123')

        auth = parse_authorization_header(signed['authorization'])
        params = auth[1]
        self.assertIn('keyId', params)
        self.assertIn('algorithm', params)
        self.assertIn('signature', params)
        self.assertEqual(params['keyId'], 'pda')
        self.assertEqual(params['algorithm'], 'hmac-sha256')
        self.assertEqual(params['signature'], 'SFlytCGpsqb/9qYaKCQklGDvwgmrwfIERFnwt+yqPJw=')


if __name__ == "__main__":
    unittest.main()
