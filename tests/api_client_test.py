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
        assert address_txs['total'] >= len(address_txs['data'])

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
        tx = client.transaction("4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b")
        assert tx and 'hash' in tx and 'confirmations' in tx
        assert tx['hash'] == "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
        assert 'enough_fee' not in tx

        # random TX 1
        tx = client.transaction("c791b82ed9af681b73eadb7a05b67294c1c3003e52d01e03775bfb79d4ac58d1")
        assert tx and 'hash' in tx and 'confirmations' in tx
        assert tx['hash'] == "c791b82ed9af681b73eadb7a05b67294c1c3003e52d01e03775bfb79d4ac58d1"
        assert tx['enough_fee'] is True
        assert tx['high_priority'] is False


if __name__ == "__main__":
    unittest.main()
