from __future__ import print_function

import unittest
import os
import binascii
import time
from bitcoin.deterministic import bip32_master_key, TESTNET_PRIVATE, MAINNET_PRIVATE, bip32_privtopub, bip32_ckd, \
    bip32_descend, bip32_deserialize
from bitcoin import safe_hexlify
import blocktrail
from mnemonic import Mnemonic


class WalletTestCase(unittest.TestCase):
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

        return blocktrail.APIClient(api_key, api_secret, testnet=True, debug=debug)

    def create_transaction_test_wallet(self, client, identifier="unittest-transaction"):
        primary_mnemonic = "give pause forget seed dance crawl situate hole keen"
        backup_mnemonic = "give pause forget seed dance crawl situate hole give"
        passphrase = "password"

        return self.create_test_wallet(client, identifier, passphrase, primary_mnemonic, backup_mnemonic)

    def create_test_wallet(self, client, identifier, passphrase, primary_mnemonic, backup_mnemonic):
        testnet = True
        vbytes = TESTNET_PRIVATE if testnet else MAINNET_PRIVATE
        key_index = 9999
        primary_seed = Mnemonic.to_seed(primary_mnemonic, passphrase)
        primary_private_key = bip32_master_key(primary_seed, vbytes=vbytes)

        primary_public_key = bip32_privtopub(bip32_ckd(primary_private_key, key_index + 2**31))

        backup_seed = Mnemonic.to_seed(backup_mnemonic, "")
        backup_public_key = bip32_privtopub(bip32_master_key(backup_seed, vbytes=vbytes))

        checksum = ""

        result = client._create_new_wallet(
            identifier=identifier,
            primary_public_key=(primary_public_key, "M/%d'" % key_index),
            backup_public_key=(backup_public_key, "M"),
            primary_mnemonic=primary_mnemonic,
            checksum=checksum,
            key_index=9999
        )

        blocktrail_public_keys = result['blocktrail_public_keys']
        key_index = result['key_index']

        return blocktrail.Wallet(
            client=client,
            identifier=identifier,
            primary_mnemonic=primary_mnemonic,
            primary_private_key=primary_private_key,
            backup_public_key=backup_public_key,
            blocktrail_public_keys=blocktrail_public_keys,
            key_index=key_index,
            testnet=testnet
        )

    def get_random_test_identifier(self):
        bytes = os.urandom(10)
        time.time()
        return "py-sdk-" + str(int(time.time())) + "-" + binascii.hexlify(bytes).decode("utf-8")

    def test_bip32(self):
        master = "tpubD9q6vq9zdP3gbhpjs7n2TRvT7h4PeBhxg1Kv9jEc1XAss7429VenxvQTsJaZhzTk54gnsHRpgeeNMbm1QTag4Wf1QpQ3gy221GDuUCxgfeZ"

        vbytes, depth, fingerprint, i, chaincode, key = bip32_deserialize(master)

        assert (safe_hexlify(key) == "022f6b9339309e89efb41ecabae60e1d40b7809596c68c03b05deb5a694e33cd26")

        assert bip32_ckd(master, "0") == "tpubDAtJthHcm9MJwmHp4r2UwSTmiDYZWHbQUMqySJ1koGxQpRNSaJdyL2Ab8wwtMm5DsMMk3v68299LQE6KhT8XPQWzxPLK5TbTHKtnrmjV8Gg"
        assert bip32_ckd(bip32_ckd(master, "0"), "0") == "tpubDDfqpEKGqEVa5FbdLtwezc6Xgn81teTFFVA69ZfJBHp4UYmUmhqVZMmqXeJBDahvySZrPjpwMy4gKfNfrxuFHmzo1r6srB4MrsDKWbwEw3d"

    def test_create_wallet(self):
        client = self.setup_api_client()

        identifier = self.get_random_test_identifier()

        wallet = self.create_transaction_test_wallet(client, identifier)

        self.cleanup_data.setdefault('wallets', []).append(wallet)

        # wallets = client.all_wallets()
        # assert len(wallets) > 0

        assert wallet.primary_mnemonic == "give pause forget seed dance crawl situate hole keen"
        assert wallet.identifier == identifier
        assert wallet.blocktrail_public_keys['9999'] == "tpubD9q6vq9zdP3gbhpjs7n2TRvT7h4PeBhxg1Kv9jEc1XAss7429VenxvQTsJaZhzTk54gnsHRpgeeNMbm1QTag4Wf1QpQ3gy221GDuUCxgfeZ"

        assert wallet.get_address_by_path("M/9999'/0/0") == "2MzyKviSL6pnWxkbHV7ecFRE3hWKfzmT8WS"

        path, address = wallet.get_new_address_pair()
        assert path == "M/9999'/0/0"
        assert address == "2MzyKviSL6pnWxkbHV7ecFRE3hWKfzmT8WS"

        path, address = wallet.get_new_address_pair()
        assert path == "M/9999'/0/1"
        assert address == "2N65RcfKHiKQcPGZAA2QVeqitJvAQ8HroHD"

        assert wallet.get_address_by_path("M/9999'/0/1") == "2N65RcfKHiKQcPGZAA2QVeqitJvAQ8HroHD"
        assert wallet.get_address_by_path("M/9999'/0/6") == "2MynrezSyqCq1x5dMPtRDupTPA4sfVrNBKq"
        assert wallet.get_address_by_path("M/9999'/0/44") == "2N5eqrZE7LcfRyCWqpeh1T1YpMdgrq8HWzh"

    def test_wallet_transaction(self):
        client = self.setup_api_client()

        wallet = client.init_wallet("unittest-transaction", "password")

        confirmed, unconfirmed = wallet.get_balance()
        assert unconfirmed + confirmed > 0
        assert confirmed > 0

        path, address = wallet.get_new_address_pair()
        assert "M/9999'/0" in path
        # assert address == "2MzyKviSL6pnWxkbHV7ecFRE3hWKfzmT8WS" # validate address

        txhash = wallet.pay([(address, blocktrail.to_satoshi(0.0001))])

        assert txhash

        time.sleep(1)

        tx = client.transaction(txhash)

        assert tx
        assert tx['hash'] == txhash


if __name__ == "__main__":
    unittest.main()