SDK_VERSION = "0.0.1"
SDK_USER_AGENT = "blocktrail-sdk-python"


from blocktrail import connection
from blocktrail import exceptions


class APIClient(object):
    def __init__(self, api_key, api_secret, network='BTC', testnet=False, api_version='v1', api_endpoint=None):
        if api_endpoint is None:
            network = ("t" if testnet else "") + network.upper()
            api_endpoint = "http://api.blocktrail.ngrok.com/%s/%s" % (api_version, network)

        self.client = connection.RestClient(api_endpoint, api_key, api_secret)

    def address(self, address):
        response = self.client.get("/address/%s" % (address, ))

        return response.json()

    def verify_address(self, address, signature):
        response = self.client.post("/address/%s/verify" % (address, ), data={'signature': signature})

        return response.json()
