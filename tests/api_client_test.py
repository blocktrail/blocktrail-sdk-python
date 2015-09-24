import unittest
import os
import binascii
import blocktrail


class ApiClientTestCase(unittest.TestCase):
    def setUp(self):
        self.cleanup_data = {}

    def tearDown(self):
        #cleanup any records that were created after each test
        client = self.setup_api_client(debug=False)

        #webhooks
        if 'webhooks' in self.cleanup_data:
            count = 0
            for webhook in self.cleanup_data['webhooks']:
                try:
                    count += int(client.delete_webhook(webhook))
                except Exception:
                    pass

    def setup_api_client(self, api_key=None, api_secret=None, debug=True):
        if api_key is None:
            api_key = os.environ.get('BLOCKTRAIL_SDK_APIKEY', 'EXAMPLE_BLOCKTRAIL_SDK_PYTHON_APIKEY')
        if api_secret is None:
            api_secret = os.environ.get('BLOCKTRAIL_SDK_APISECRET', 'EXAMPLE_BLOCKTRAIL_SDK_PYTHON_APISECRET')

        return blocktrail.APIClient(api_key, api_secret, debug=debug)

    def test_coin_value(self):
        assert 1 == blocktrail.to_satoshi(0.00000001)
        assert 1.0, blocktrail.to_btc(100000000)

        assert 123456789, blocktrail.to_satoshi(1.23456789)
        assert 1.23456789, blocktrail.to_btc(123456789)
    
    def test_auth(self):
        client = self.setup_api_client(api_secret="FAILSECRET", debug=False)

        assert client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")

        with self.assertRaises(blocktrail.exceptions.InvalidCredentials):
            client.verify_address("16dwJmR4mX5RguGrocMfN9Q9FR2kZcLw2z", "HPMOHRgPSMKdXrU6AqQs/i9S7alOakkHsJiqLGmInt05Cxj6b/WhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk=")

        client = self.setup_api_client(api_key="FAILKEY", debug=False)

        with self.assertRaises(blocktrail.exceptions.InvalidCredentials):
            client.verify_address("16dwJmR4mX5RguGrocMfN9Q9FR2kZcLw2z", "HPMOHRgPSMKdXrU6AqQs/i9S7alOakkHsJiqLGmInt05Cxj6b/WhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk=")

        client = self.setup_api_client()
        try:
            client.verify_address("16dwJmR4mX5RguGrocMfN9Q9FR2kZcLw2z", "HPMOHRgPSMKdXrU6AqQs/i9S7alOakkHsJiqLGmInt05Cxj6b/WhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk=")
        except blocktrail.exceptions.InvalidCredentials:
            assert False, "InvalidCredentials raised"
        except Exception:
            assert True, "Other Exception is fine" # we're not testing verify_address, we're testing HMAC!

    def test_address(self):
        client = self.setup_api_client()

        # address info
        address = client.address("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")
        assert address and 'address' in address
        assert address['address'] == "1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp"

        # address transactions
        address_txs = client.address_transactions("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp", limit=23)
        assert address_txs and 'total' in address_txs and 'data' in address_txs
        assert len(address_txs['data']) == 23

        # address unconfirmed transactions
        address_txs = client.address_unconfirmed_transactions("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp", limit=23)
        assert address_txs and 'total' in address_txs and 'data' in address_txs
        # assert address_txs['total'] >= len(address_txs['data'])

        # address unspent outputs
        address_utxo = client.address_unspent_outputs("1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp", limit=23)
        assert address_utxo and 'total' in address_utxo and 'data' in address_utxo
        assert address_utxo['total'] >= len(address_utxo['data'])

        verify = client.verify_address("16dwJmR4mX5RguGrocMfN9Q9FR2kZcLw2z", "HPMOHRgPSMKdXrU6AqQs/i9S7alOakkHsJiqLGmInt05Cxj6b/WhS7kJxbIQxKmDW08YKzoFnbVZIoTI2qofEzk=")
        assert verify and verify['result']

    def test_block(self):
        client = self.setup_api_client()

        # block info
        block = client.block("000000000000034a7dedef4a161fa058a2d67a173a90155f3a2fe6fc132e0ebf")
        assert block and 'hash' in block
        assert block['hash'] == "000000000000034a7dedef4a161fa058a2d67a173a90155f3a2fe6fc132e0ebf"

        # block info by height
        block = client.block(200000)
        assert block and 'hash' in block
        assert block['hash'] == "000000000000034a7dedef4a161fa058a2d67a173a90155f3a2fe6fc132e0ebf"

        # block transactions
        block_txs = client.block_transactions("000000000000034a7dedef4a161fa058a2d67a173a90155f3a2fe6fc132e0ebf", limit=23)
        assert block_txs and 'total' in block_txs and 'data' in block_txs
        assert len(block_txs['data']) == 23

        # all blocks
        blocks = client.all_blocks(page=2, limit=23)
        assert blocks and 'total' in blocks and 'data' in blocks
        assert len(blocks['data']) == 23
        assert 'hash' in blocks['data'][0]
        assert 'hash' in blocks['data'][1]
        assert blocks['data'][0]['hash'] == '000000000cd339982e556dfffa9de94744a4135c53eeef15b7bcc9bdeb9c2182'
        assert blocks['data'][1]['hash'] == '00000000fc051fbbce89a487e811a5d4319d209785ea4f4b27fc83770d1e415f'

        # latest block
        block = client.block_latest()
        assert block and 'hash' in block

    def test_transaction(self):
        client = self.setup_api_client()

        # coinbase TX
        tx = client.transaction("0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098")
        assert tx and 'hash' in tx and 'confirmations' in tx
        assert tx['hash'] == "0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098"
        assert tx['enough_fee'] is None

        # random TX 1
        tx = client.transaction("c791b82ed9af681b73eadb7a05b67294c1c3003e52d01e03775bfb79d4ac58d1")
        assert tx and 'hash' in tx and 'confirmations' in tx
        assert tx['hash'] == "c791b82ed9af681b73eadb7a05b67294c1c3003e52d01e03775bfb79d4ac58d1"
        assert tx['enough_fee'] is True
        assert tx['high_priority'] is False

    def test_webhooks(self):
        client = self.setup_api_client()

        # keep track of all webhooks created for cleanup
        self.cleanup_data['webhooks'] = []

        # create a webhook with a custom identifier (randomly generated)
        bytes = os.urandom(10)
        identifier_1 = binascii.hexlify(bytes).decode("utf-8")
        result = client.setup_webhook("https://www.blocktrail.com/webhook-test", identifier_1)
        assert result and 'url' in result and 'identifier' in result
        assert result['url'] == "https://www.blocktrail.com/webhook-test"
        assert result['identifier'] == identifier_1

        webhookID1 = result['identifier']
        self.cleanup_data['webhooks'].append(webhookID1)

        # create a webhook without a custom identifier
        result = client.setup_webhook("https://www.blocktrail.com/webhook-test")
        assert result and 'url' in result and 'identifier' in result
        assert result['url'] == "https://www.blocktrail.com/webhook-test"
        assert len(result['identifier']) > 0

        webhookID2 = result['identifier']
        self.cleanup_data['webhooks'].append(webhookID2)

        # get all webhooks
        result = client.all_webhooks()
        assert result and 'data' in result and 'total' in result
        assert result['total'] >= 2
        assert len(result['data']) >= 2

        assert 'url' in result['data'][0]
        assert 'url' in result['data'][1]


        # get a single webhook
        result = client.webhook(webhookID1)
        assert result and 'url' in result and 'identifier' in result
        assert result['url'] == "https://www.blocktrail.com/webhook-test"
        assert result['identifier'] == webhookID1

        # delete a webhook
        assert client.delete_webhook(webhookID1)

        # update a webhook
        bytes = os.urandom(10)
        new_identifier = binascii.hexlify(bytes).decode("utf-8")
        result = client.update_webhook(webhookID2, "https://www.blocktrail.com/new-webhook-url", new_identifier)
        assert result and 'url' in result and 'identifier' in result
        assert result['url'] == "https://www.blocktrail.com/new-webhook-url"
        assert result['identifier'] == new_identifier
        webhookID2 = result['identifier']
        self.cleanup_data['webhooks'].append(webhookID2)

        # add webhook event subscription (address-transactions)
        result = client.subscribe_address_transactions(webhookID2, "1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp", 2)
        assert result
        assert result['event_type'] == 'address-transactions'
        assert result['address'] == '1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp'
        assert result['confirmations'] == 2

        # add webhook event subscription (block)
        result = client.subscribe_new_blocks(webhookID2)
        assert result
        assert result['event_type'] == 'block'

        # add webhook event subscription (transactions)
        result = client.subscribe_transaction(webhookID2,
                                              "6a46bf067704284340e64cb963d816b152643e0c156204632f58aec1d751d145", 2)
        assert result
        assert result['event_type'] == 'transaction'
        assert result['address'] is None
        assert result['transaction'] == '6a46bf067704284340e64cb963d816b152643e0c156204632f58aec1d751d145'
        assert result['confirmations'] == 2

        # get webhook's event subscriptions
        result = client.webhook_events(webhookID2)
        assert result and 'data' in result and 'total' in result
        assert result['total'] == 3
        assert len(result['data']) == 3

        assert result['data'][0]['event_type'] == 'address-transactions'
        assert result['data'][1]['event_type'] == 'block'
        assert result['data'][2]['event_type'] == 'transaction'

        # unsubscribe webhook event (address-transaction)
        assert client.unsubscribe_address_transactions(webhookID2, "1dice8EMZmqKvrGE4Qc9bUFf9PX3xaYDp")

        # unsubscribe webhook event (block)
        assert client.unsubscribe_new_blocks(webhookID2)

        # unsubscribe webhook event (transaction)
        assert client.unsubscribe_transaction(webhookID2,
                                              "6a46bf067704284340e64cb963d816b152643e0c156204632f58aec1d751d145")


        # batch create webhook events (address-transactions)
        batch_data = [
            {
                'event_type': 'address-transactions',
                'address': '18FA8Tn54Hu8fjn7kkfAygPoGEJLHMbHzo',
                'confirmations': 1
            },
            {
                'address': '1LUCKYwD6V9JHVXAFEEjyQSD4Dj5GLXmte',
                'confirmations': 1
            },
            {
                'address': '1qMBuZnrmGoAc2MWyTnSgoLuWReDHNYyF'
            }
        ]
        result = client.batch_subscribe_address_transactions(webhookID2, batch_data)
        assert result
        result = client.webhook_events(webhookID2)
        assert result['total'] == 3
        assert len(result['data']) == 3
        assert result['data'][2]['address'] == batch_data[2]['address']


        # cleanup - @todo needs to be put in a cleanup class and run regardless of the test progress
        #assert client.delete_webhook(webhookID2)

    def test_price_index(self):
        client = self.setup_api_client()

        result = client.price()
        assert result and 'USD' in result

    def test_verify_message(self):
        client = self.setup_api_client()

        address = "1F26pNMrywyZJdr22jErtKcjF8R3Ttt55G"
        message = address
        signature = "H85WKpqtNZDrajOnYDgUY+abh0KCAcOsAIOQwx2PftAbLEPRA7mzXA/CjXRxzz0MC225pR/hx02Vf2Ag2x33kU4="

        result = client.verify_message(message, address, signature)
        assert result


if __name__ == "__main__":
    unittest.main()
