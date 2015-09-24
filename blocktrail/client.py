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

    def all_webhooks(self, page=1, limit=20):
        """
        get all webhooks (paginated)

        :param int      page:            pagination page, starting at 1
        :param int      limit:           the amount of webhooks per page, can be between 1 and 200
        :rtype: dict
        """

        response = self.client.get("/webhooks", params={'page': page, 'limit': limit})

        return response.json()

    def webhook(self, identifier):
        """
        get a webhook by it's identifier

        :param str      identifier:      the webhook identifier
        :rtype: dict
        """

        response = self.client.get("/webhook/%s" % (identifier, ))

        return response.json()

    def setup_webhook(self, url, identifier=None):
        """
        create a new webhook

        :param str      url:            the url to receive the webhook events
        :param str      identifier:     a unique identifier to associate with this webhook (optional)
        :rtype: dict
        """
        response = self.client.post("/webhook", data={'url': url, 'identifier': identifier}, auth=True)

        return response.json()

    def update_webhook(self, identifier, new_url=None, new_identifier=None):
        """
        update an existing webhook

        :param str      identifier:     the webhook identifier
        :param str      new_url:        the new webhook url
        :param str      new_identifier: the new webhook identifier
        :rtype: dict
        """
        response = self.client.put("/webhook/%s" % (identifier, ),
                                   data={'url': new_url, 'identifier': new_identifier},
                                   auth=True)

        return response.json()

    def delete_webhook(self, identifier):
        """
        deletes an existing webhook and any event subscriptions associated with it

        :param str      identifier:     the webhook identifier
        :rtype: dict
        """
        response = self.client.delete("/webhook/%s" % (identifier, ), auth=True)

        return response.json()

    def webhook_events(self, identifier, page=1, limit=20):
        """
        get a paginated list of all the events a webhook is subscribed to

        :param str      identifier:     the webhook identifier
        :param int      page:           pagination page, starting at 1
        :param int      limit:          the amount of webhooks per page, can be between 1 and 200
        :rtype: dict
        """

        response = self.client.get("/webhook/%s/events" % (identifier, ), params={'page': page, 'limit': limit})

        return response.json()

    def subscribe_address_transactions(self, identifier, address, confirmations=6):
        """
        subscribes a webhook to transaction events on a particular address

        :param str      identifier:     the webhook identifier
        :param str      address:        the address hash
        :param str      confirmations:  the amount of confirmations to send
        :rtype: dict
        """
        response = self.client.post(
            "/webhook/%s/events" % (identifier, ),
            data={
                'event_type': 'address-transactions',
                'address': address,
                'confirmations': confirmations
            },
            auth=True
        )

        return response.json()

    def batch_subscribe_address_transactions(self, identifier, batch_data):
        """
        batch subscribes a webhook to multiple transaction events

        :param str      identifier:     the webhook identifier
        :param list     batch_data:
        :rtype: dict
        """
        for record in batch_data:
            record['event_type'] = 'address-transactions'

        response = self.client.post("/webhook/%s/events/batch" % (identifier, ), data=batch_data, auth=True)

        return response.json()

    def subscribe_new_blocks(self, identifier):
        """
        subscribes a webhook to new blocks

        :param str      identifier:     the webhook identifier
        :rtype: dict
        """
        response = self.client.post(
            "/webhook/%s/events" % (identifier, ),
            data={
                'event_type': 'block'
            },
            auth=True
        )

        return response.json()

    def subscribe_transaction(self, identifier, transaction, confirmations=6):
        """
        subscribes a webhook to events on a particular transaction

        :param str      identifier:     the webhook identifier
        :param str      transaction:    the transaction hash
        :param str      confirmations:  the amount of confirmations to send
        :rtype: dict
        """
        response = self.client.post(
            "/webhook/%s/events" % (identifier, ),
            data={
                'event_type': 'transaction',
                'transaction': transaction,
                'confirmations': confirmations
            },
            auth=True
        )

        return response.json()

    def unsubscribe_address_transactions(self, identifier, address):
        """
        unsubscribes a webhook to transaction events from a particular address

        :param str      identifier:     the webhook identifier
        :param str      address:        the address hash
        :rtype: dict
        """
        response = self.client.delete("/webhook/%s/address-transactions/%s" % (identifier, address), auth=True)

        return response.json()

    def unsubscribe_new_blocks(self, identifier):
        """
        unsubscribes a webhook from new blocks

        :param str      identifier:     the webhook identifier
        :rtype: dict
        """
        response = self.client.delete("/webhook/%s/block" % (identifier, ), auth=True)

        return response.json()

    def unsubscribe_transaction(self, identifier, transaction):
        """
        unsubscribes a webhook to to events on a particular transaction

        :param str      identifier:     the webhook identifier
        :param str      transaction:        the address hash
        :rtype: dict
        """
        response = self.client.delete("/webhook/%s/transaction/%s" % (identifier, transaction), auth=True)

        return response.json()

    def price(self):
        """
        get the current price index

        :rtype: dict
        """

        response = self.client.get("/price")

        return response.json()

    def verify_message(self, message, address, signature):
        """
        verify message signed bitcoin-core style

        :param str      message:
        :param str      address:
        :param str      signature:
        :rtype: dict
        """

        response = self.client.post("/verify_message", dict(
            message=message,
            address=address,
            signature=signature
        ))

        return response.json()['result']
