from __future__ import print_function

import unittest
import os
import binascii
import time
import blocktrail
from bitcoin.core import x, b2x, lx
from blocktrail.exceptions import ObjectNotFound
from pycoin.key.BIP32Node import BIP32Node
from mnemonic import Mnemonic


class WalletTestCase(unittest.TestCase):
    def setUp(self):
        self.cleanup_data = {}

    def tearDown(self):
        # cleanup any records that were created after each test
        client = self.setup_api_client(debug=False)

        # webhooks
        for webhook in self.cleanup_data.get('webhooks', []):
            try:
                client.delete_webhook(webhook)
            except Exception:
                pass

        # wallets
        for wallet in self.cleanup_data.get('wallets', []):
            try:
                pass
                # @TODO: delete_wallet is not implemented yet
                # wallet.delete_wallet()
            except Exception:
                pass

    def setup_api_client(self, api_key=None, api_secret=None, debug=False):
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

    def create_discovery_test_wallet(self, client, identifier="unittest-transaction", passphrase="password"):
        primary_mnemonic = "give pause forget seed dance crawl situate hole kingdom"
        backup_mnemonic = "give pause forget seed dance crawl situate hole course"

        return self.create_test_wallet(client, identifier, passphrase, primary_mnemonic, backup_mnemonic)

    def create_test_wallet(self, client, identifier, passphrase, primary_mnemonic, backup_mnemonic):
        testnet = True
        netcode = "XTN" if testnet else "BTC"
        key_index = 9999
        primary_seed = Mnemonic.to_seed(primary_mnemonic, passphrase)
        primary_private_key = BIP32Node.from_master_secret(primary_seed, netcode=netcode)

        primary_public_key = primary_private_key.subkey_for_path("%d'.pub" % key_index)

        backup_seed = Mnemonic.to_seed(backup_mnemonic, "")
        backup_public_key = BIP32Node.from_master_secret(backup_seed, netcode=netcode).public_copy()

        checksum = blocktrail.APIClient.create_checksum(primary_private_key)

        result = client._create_new_wallet(
            identifier=identifier,
            primary_public_key=(primary_public_key.as_text(), "M/%d'" % key_index),
            backup_public_key=(backup_public_key.as_text(), "M"),
            primary_mnemonic=primary_mnemonic,
            checksum=checksum,
            key_index=key_index
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

        key = BIP32Node.from_hwif(master)

        self.assertEqual(b2x(key.sec()), "022f6b9339309e89efb41ecabae60e1d40b7809596c68c03b05deb5a694e33cd26")

        self.assertEqual(key.subkey_for_path("0").hwif(), "tpubDAtJthHcm9MJwmHp4r2UwSTmiDYZWHbQUMqySJ1koGxQpRNSaJdyL2Ab8wwtMm5DsMMk3v68299LQE6KhT8XPQWzxPLK5TbTHKtnrmjV8Gg")
        self.assertEqual(key.subkey_for_path("0/0").hwif(), "tpubDDfqpEKGqEVa5FbdLtwezc6Xgn81teTFFVA69ZfJBHp4UYmUmhqVZMmqXeJBDahvySZrPjpwMy4gKfNfrxuFHmzo1r6srB4MrsDKWbwEw3d")

        key = BIP32Node.from_master_secret(x("000102030405060708090a0b0c0d0e0f"), "XTN")

        self.assertEqual(key.subkey_for_path("0'/1/2'/2/1000000000").hwif(), "tpubDHNy3kAG39ThyiwwsgoKY4iRenXDRtce8qdCFJZXPMCJg5dsCUHayp84raLTpvyiNA9sXPob5rgqkKvkN8S7MMyXbnEhGJMW64Cf4vFAoaF")

    def test_create_wallet(self):
        client = self.setup_api_client()

        identifier = self.get_random_test_identifier()

        wallet = self.create_transaction_test_wallet(client, identifier)

        self.cleanup_data.setdefault('wallets', []).append(wallet)

        wallets = client.all_wallets()
        self.assertTrue(len(wallets) > 0)

        self.assertEqual(wallet.primary_mnemonic, "give pause forget seed dance crawl situate hole keen")
        self.assertEqual(wallet.identifier, identifier)
        self.assertEqual(wallet.blocktrail_public_keys['9999'].as_text(), "tpubD9q6vq9zdP3gbhpjs7n2TRvT7h4PeBhxg1Kv9jEc1XAss7429VenxvQTsJaZhzTk54gnsHRpgeeNMbm1QTag4Wf1QpQ3gy221GDuUCxgfeZ")

        self.assertEqual(wallet.get_address_by_path("M/9999'/0/0"), "2MzyKviSL6pnWxkbHV7ecFRE3hWKfzmT8WS")

        path, address = wallet.get_new_address_pair()
        self.assertEqual(path, "M/9999'/0/0")
        self.assertEqual(address, "2MzyKviSL6pnWxkbHV7ecFRE3hWKfzmT8WS")

        path, address = wallet.get_new_address_pair()
        self.assertEqual(path, "M/9999'/0/1")
        self.assertEqual(address, "2N65RcfKHiKQcPGZAA2QVeqitJvAQ8HroHD")

        self.assertEqual(wallet.get_address_by_path("M/9999'/0/1"), "2N65RcfKHiKQcPGZAA2QVeqitJvAQ8HroHD")
        self.assertEqual(wallet.get_address_by_path("M/9999'/0/6"), "2MynrezSyqCq1x5dMPtRDupTPA4sfVrNBKq")
        self.assertEqual(wallet.get_address_by_path("M/9999'/0/44"), "2N5eqrZE7LcfRyCWqpeh1T1YpMdgrq8HWzh")

    def test_wallet_transaction(self):
        client = self.setup_api_client()

        wallet = client.init_wallet("unittest-transaction", "password")

        confirmed, unconfirmed = wallet.get_balance()
        self.assertGreater(unconfirmed + confirmed, 0)
        self.assertGreater(confirmed, 0)

        path, address = wallet.get_new_address_pair()
        self.assertTrue("M/9999'/0" in path)
        # self.assertEqual(address, "2MzyKviSL6pnWxkbHV7ecFRE3hWKfzmT8WS" # validate address)

        value = blocktrail.to_satoshi(0.0002)
        txhash = wallet.pay([(address, value)])

        self.assertTrue(txhash)

        time.sleep(1)

        tx = client.transaction(txhash)

        self.assertTrue(tx)
        self.assertEqual(tx['hash'], txhash)
        self.assertTrue(len(tx['outputs']) <= 2)
        self.assertTrue(value in map(lambda o: o['value'], tx['outputs']))

    def test_discovery_and_key_index_upgrade(self):
        client = self.setup_api_client()

        identifier = self.get_random_test_identifier()

        wallet = self.create_discovery_test_wallet(client, identifier)

        self.cleanup_data.setdefault('wallets', []).append(wallet)

        self.assertEqual(wallet.primary_mnemonic, "give pause forget seed dance crawl situate hole kingdom")
        self.assertEqual(wallet.identifier, identifier)
        self.assertEqual(wallet.blocktrail_public_keys['9999'].as_text(), "tpubD9q6vq9zdP3gbhpjs7n2TRvT7h4PeBhxg1Kv9jEc1XAss7429VenxvQTsJaZhzTk54gnsHRpgeeNMbm1QTag4Wf1QpQ3gy221GDuUCxgfeZ")

        self.assertEqual(wallet.get_address_by_path("M/9999'/0/0"), "2Mtfn5S9tVWnnHsBQixCLTsCAPFHvfhu6bM")

        path, address = wallet.get_new_address_pair()
        self.assertEqual(path, "M/9999'/0/0")
        self.assertEqual(address, "2Mtfn5S9tVWnnHsBQixCLTsCAPFHvfhu6bM")

        path, address = wallet.get_new_address_pair()
        self.assertEqual(path, "M/9999'/0/1")
        self.assertEqual(address, "2NG49GDkm5qCYvDFi4cxAnkSho8qLbEz6C4")

        confirmed, unconfirmed = wallet.do_discovery(gap=50)
        self.assertGreater(confirmed + unconfirmed, 0)

        wallet.upgrade_key_index(10000)

        self.assertEqual(wallet.blocktrail_public_keys['10000'].as_text(), "tpubD9m9hziKhYQExWgzMUNXdYMNUtourv96sjTUS9jJKdo3EDJAnCBJooMPm6vGSmkNTNAmVt988dzNfNY12YYzk9E6PkA7JbxYeZBFy4XAaCp")

        self.assertEqual(wallet.get_address_by_path("M/10000'/0/0"), "2N9ZLKXgs12JQKXvLkngn7u9tsYaQ5kXJmk")

        path, address = wallet.get_new_address_pair()
        self.assertEqual(path, "M/10000'/0/0")
        self.assertEqual(address, "2N9ZLKXgs12JQKXvLkngn7u9tsYaQ5kXJmk")

    def test_list_wallet_txs_addrs(self):
        client = self.setup_api_client()

        wallet = client.init_wallet("unittest-transaction", "password")

        txs = wallet.transactions(page=1, limit=23)

        self.assertEqual(len(txs['data']), 23)
        self.assertEqual(txs['data'][0]['hash'], '2cb21783635a5f22e9934b8c3262146b42d251dfb14ee961d120936a6c40fe89')

        addresses = wallet.addresses(page=1, limit=23)

        self.assertEqual(len(addresses['data']), 23)
        self.assertEqual(addresses['data'][0]['address'], '2MzyKviSL6pnWxkbHV7ecFRE3hWKfzmT8WS')

    def test_bad_password_wallet(self):
        client = self.setup_api_client()

        identifier = self.get_random_test_identifier()

        wallet = self.create_discovery_test_wallet(client, identifier, "badpassword")

        self.cleanup_data.setdefault('wallets', []).append(wallet)

        self.assertEqual(wallet.primary_mnemonic, "give pause forget seed dance crawl situate hole kingdom")
        self.assertEqual(wallet.identifier, identifier)
        self.assertEqual(wallet.blocktrail_public_keys['9999'].as_text(), "tpubD9q6vq9zdP3gbhpjs7n2TRvT7h4PeBhxg1Kv9jEc1XAss7429VenxvQTsJaZhzTk54gnsHRpgeeNMbm1QTag4Wf1QpQ3gy221GDuUCxgfeZ")

        self.assertEqual(wallet.get_address_by_path("M/9999'/0/0"), "2N9SGrV4NKRjdACYvHLPpy2oiPrxTPd44rg")

        path, address = wallet.get_new_address_pair()
        self.assertEqual(path, "M/9999'/0/0")
        self.assertEqual(address, "2N9SGrV4NKRjdACYvHLPpy2oiPrxTPd44rg")

        path, address = wallet.get_new_address_pair()
        self.assertEqual(path, "M/9999'/0/1")
        self.assertEqual(address, "2NDq3DRy9E3YgHDA3haPJj3FtUS6V93avkf")

        confirmed, unconfirmed = wallet.do_discovery(gap=50)
        self.assertEqual(confirmed + unconfirmed, 0)

    def test_new_blank_wallet(self):
        client = self.setup_api_client()

        identifier = self.get_random_test_identifier()

        # wallet shouldn't exist yet
        wallet = None
        try:
            wallet = client.init_wallet(identifier, 'password')
        except ObjectNotFound as e:
            pass
        self.assertFalse(wallet)

        # create wallet
        wallet, primary_mnemonic, backup_mnemonic, blocktrail_pubkeys = client.create_new_wallet(identifier, "password", 9999)

        self.cleanup_data.setdefault('wallets', []).append(wallet)

        # wallet shouldn't be able to pay
        txhash = None
        try:
            txhash = wallet.pay({"2N6Fg6T74Fcv1JQ8FkPJMs8mYmbm9kitTxy": blocktrail.to_satoshi(0.001)})
        except:
            pass
        self.assertFalse(txhash)

        # same wallet with bad password shouldn't be initialized
        wallet = None
        try:
            wallet = client.init_wallet(identifier, "badpassword")
        except:
            pass
        self.assertFalse(wallet)

    def test_webhook_for_wallet(self):
        client = self.setup_api_client()

        identifier = self.get_random_test_identifier()

        # create wallet
        wallet, primary_mnemonic, backup_mnemonic, blocktrail_pubkeys = client.create_new_wallet(identifier, "password", 9999)

        self.cleanup_data.setdefault('wallets', []).append(wallet)

        confirmed, unconfirmed = wallet.get_balance()

        self.assertEqual(confirmed + unconfirmed, 0)

        webhook = wallet.setup_webhook("https://www.blocktrail.com/webhook-test")
        self.assertEqual(webhook['url'], "https://www.blocktrail.com/webhook-test")
        self.assertEqual(webhook['identifier'], "WALLET-%s" % (wallet.identifier, ))

        self.assertTrue(wallet.delete_webhook())

        webhook_identifier = self.get_random_test_identifier()
        webhook = wallet.setup_webhook("https://www.blocktrail.com/webhook-test", identifier=webhook_identifier)
        self.assertEqual(webhook['url'], "https://www.blocktrail.com/webhook-test")
        self.assertEqual(webhook['identifier'], webhook_identifier)

        path, address = wallet.get_new_address_pair()

        events = client.webhook_events(webhook_identifier)

        self.assertIn(address, [event['address'] for event in events['data']])

        # @TODO: delete_wallet is not implemented yet
        # self.assertTrue(wallet.delete_wallet())

        # webhook should already be deleted so we shouldn't be able to delete it again
        # deleted = None
        # try:
        #     deleted = wallet.delete_webhook(webhook_identifier)
        # except:
        #     pass

        # self.assertFalse(deleted)


if __name__ == "__main__":
    unittest.main()
