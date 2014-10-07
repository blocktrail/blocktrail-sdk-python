SDK_VERSION = "0.0.1"
SDK_USER_AGENT = "blocktrail-sdk-python"


from blocktrail import connection
from blocktrail import exceptions


class APIClient(object):
    def __init__(self, api_key, api_secret, network='BTC', testnet=False, api_version='v1', api_endpoint=None):
        """
        :param str      api_key:        the API_KEY to use for authentication
        :param str      api_secret:     the API_SECRET to use for authentication
        :param str      network:        the crypto network to consume (eg BTC, LTC, etc)
        :param bool     testnet:        testnet network yes/no
        :param str      api_version:    the version of the API to consume
        :param str      api_endpoint:   overwrite the endpoint used
                                         this will cause the :network, :testnet and :api_version to be ignored!
        """

        if api_endpoint is None:
            network = ("t" if testnet else "") + network.upper()
            api_endpoint = "http://api.blocktrail.ngrok.com/%s/%s" % (api_version, network)

        self.client = connection.RestClient(api_endpoint, api_key, api_secret)

    def address(self, address):
        """
        :param str     address:        the address hash
        :rtype: dict
        """
        response = self.client.get("/address/%s" % (address, ))

        return response.json()

    def address_transactions(self, address, page=1, limit=20, sort_dir='asc'):
        response = self.client.get("/address/%s/transactions" % (address, ), params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def verify_address(self, address, signature):
        """
        :param str      address:        the address hash
        :param str      signature:      signature generated with PK with message being the :address
        :rtype: dict
        """
        response = self.client.post("/address/%s/verify" % (address, ), data={'signature': signature})

        return response.json()
