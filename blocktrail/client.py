from blocktrail import connection


class APIClient(object):
    def __init__(self, api_key, api_secret, network='BTC', testnet=False, api_version='v1', api_endpoint=None, debug=False):
        """
        :param str      api_key:        the API_KEY to use for authentication
        :param str      api_secret:     the API_SECRET to use for authentication
        :param str      network:        the crypto network to consume (eg BTC, LTC, etc)
        :param bool     testnet:        testnet network yes/no
        :param str      api_version:    the version of the API to consume
        :param str      api_endpoint:   overwrite the endpoint used
                                         this will cause the :network, :testnet and :api_version to be ignored!
        :param bool     debug:          print debug information when requests fail
        """

        if api_endpoint is None:
            network = ("t" if testnet else "") + network.upper()
            api_endpoint = "https://api.blocktrail.com/%s/%s" % (api_version, network)

        self.client = connection.RestClient(api_endpoint=api_endpoint, api_key=api_key, api_secret=api_secret, debug=debug)

    def address(self, address):
        """
        get a single address

        :param str      address:        the address hash
        :rtype: dict
        """
        response = self.client.get("/address/%s" % (address, ))

        return response.json()

    def address_transactions(self, address, page=1, limit=20, sort_dir='asc'):
        """
        get all transactions for an address (paginated)

        :param str      address:        the address hash
        :param int      page:           pagination page, starting at 1
        :param int      limit:          the amount of transactions per page, can be between 1 and 200
        :param str      address:        sorted ASC or DESC (on time)
        :rtype: dict
        """

        response = self.client.get("/address/%s/transactions" % (address, ), params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def address_unconfirmed_transactions(self, address, page=1, limit=20, sort_dir='asc'):
        """
        get all unconfirmed transactions for an address (paginated)

        :param str      address:        the address hash
        :param int      page:           pagination page, starting at 1
        :param int      limit:          the amount of transactions per page, can be between 1 and 200
        :param str      sort_dir:       sorted ASC or DESC (on time)
        :rtype: dict
        """
        response = self.client.get("/address/%s/unconfirmed-transactions" % (address, ), params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def address_unspent_outputs(self, address, page=1, limit=20, sort_dir='asc'):
        """
        get all inspent outputs for an address (paginated)

        :param str      address:        the address hash
        :param int      page:           pagination page, starting at 1
        :param int      limit:          the amount of transactions per page, can be between 1 and 200
        :param str      sort_dir:       sorted ASC or DESC (on time)
        :rtype: dict
        """
        response = self.client.get("/address/%s/unspent-outputs" % (address, ), params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def verify_address(self, address, signature):
        """
        verify ownership of an address

        :param str      address:        the address hash
        :param str      signature:      signature generated with PK with message being the :address
        :rtype: dict
        """
        response = self.client.post("/address/%s/verify" % (address, ), data={'signature': signature}, auth=True)

        return response.json()

    def all_blocks(self, page=1, limit=20, sort_dir='asc'):
        """
        get all blocks (paginated)

        :param int      page:            pagination page, starting at 1
        :param int      limit:           the amount of transactions per page, can be between 1 and 200
        :param str      sort_dir:        sorted ASC or DESC (on time)
        :rtype: dict
        """

        response = self.client.get("/all-blocks", params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def block_latest(self):
        """
        get the latest block

        :rtype: dict
        """
        response = self.client.get("/block/latest")

        return response.json()

    def block(self, block):
        """
        get a block

        :param str|int  block:           the block hash or block height
        :rtype: dict
        """

        response = self.client.get("/block/%s" % (block, ))

        return response.json()

    def block_transactions(self, block, page=1, limit=20, sort_dir='asc'):
        """
        get all transactions for a block (paginated)

        :param str|int  block:           the block hash or block height
        :param int      page:            pagination page, starting at 1
        :param int      limit:           the amount of transactions per page, can be between 1 and 200
        :param str      sort_dir:        sorted ASC or DESC (on time)
        :rtype: dict
        """

        response = self.client.get("/block/%s/transactions" % (block, ), params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def transaction(self, txhash):
        """
        get a single transaction

        :param str      txhash:          the transaction hash
        :rtype: dict
        """

        response = self.client.get("/transaction/%s" % (txhash, ))

        return response.json()
